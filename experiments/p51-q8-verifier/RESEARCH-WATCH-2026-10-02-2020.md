# Project 51 research watch — 2026-10-02 20:20 ET

Freshness boundary entering: **2026-10-02 23:25:36 UTC**
Cutoff: **2026-10-03 00:20:49 UTC**

## Decision

**No numeric primary-Windows target movement.**

Current exact-box state remains:
- Strata baseline: **0.1.37**;
- IQ3_S + native262K physical fit/admission: **~95%**;
- Windows 16-GB/64-GB full-context admission: **~90%**;
- 8 h / 24 h zero-stall: **~75% / ~55%**;
- #481-style automatic containment/no-manual-service-restart: **~85%**;
- conversation parking OFF for the initial baseline;
- explicit `reasoning_budget_tokens` for high/xhigh;
- frozen expert residency for source/AA qualification.

This pass changes the **Apple/TurboQuant interpretation** and adds one optional Strata lifecycle feature:

1. **oMLX now has live QSA TurboQuant evidence**, but it does not move the first-prefill context ceiling.
   Post-prefill 4-bit TurboQuant reduces an ~84.8K request's measured resident footprint from 55.8 -> 49.2 GB on a
   64-GB M4 Pro, while an attempted quantize-during-prefill phase still did not move the ceiling. Project 51 must not
   count KV compression as context-capacity credit until cold-prefill transient memory also clears.

2. **oMLX streamed experts corrects an earlier 200K+ single-64GB projection down to ~121-122K.**
   This is a single M4 Pro / oQ2 / oMLX result, not the dual-M1/TB4 target, so the dual-node production target does
   not move. It does kill any assumption that one 64-GB Apple node gets 200K merely by streaming experts/TQ.

3. **Strata #563 can give the expert-cache VRAM back while keeping the model loaded.**
   Useful for a shared workstation, but keep it OFF in the certified inference baseline: if another app still owns
   VRAM when refill occurs, WDDM can spill and decode can fall to ~10-17 TG.

No new Strata release beyond 0.1.37. No new DASLab long-agent/xhigh IQ3_S quality table. No TurboQuant-repo change.

## NEW — Strata #563: hot expert-cache VRAM release/refill

PR:
https://github.com/Niko1221/Strata/pull/563

Created **2026-10-02 23:29:52 UTC**.

Opt-in `--expert-cache-release` uses CUDA VMM for the expert-cache arena:
- RELEASE unmaps/frees the physical expert-cache VRAM while preserving the virtual addresses and model/session state;
- REFILL remaps the same addresses and copies the remembered experts back;
- a request arriving while released automatically refills first;
- optional `--cache-release-idle SECONDS` releases after idle time.

RTX 3090 / Windows / Flash-Next IQ2_XS:
- VRAM given back: **14.5 GiB** in ~50 ms;
- refill: **1.7-2.5 s**;
- 3 release/refill cycles: 0 / 10,800 refilled slots differed from the host copy;
- post-refill decode: ~72 TG.

Important limit:
- if another program still occupies the VRAM, Windows/WDDM can push the refill into shared system memory;
- the same setup then decoded at only **~10-17 TG** until the other program released VRAM.

Project-51 decision:
- feature stays **OFF** for the primary certification baseline;
- potentially useful later for an inference workstation that must temporarily yield the GPU;
- if enabled, qualification must record WDDM dedicated/shared usage after every refill before accepting a request.

No physical-fit or TG-center change.

## UPDATE — oMLX #3436: real QSA TurboQuant works, but post-prefill savings do not prove a larger ceiling

PR:
https://github.com/jundot/omlx/pull/3436

Older PR updated in this strict window.

It fixes two reasons TurboQuant previously failed to engage on Qwen3.8/Qwen4Exp QSA:
- the vendored recurrent `ArraysCache` class failed the eligibility allowlist;
- QSA's custom KV cache was not recognized by the existing TurboQuant conversion path.

The new QSA-specific TurboQuant cache preserves the full-precision indexer sideband while quantizing QSA K/V.

Live M4 Pro / 64 GB result:
- request: **84,839 tokens**;
- prefill peak: **55.8 GB**;
- post-prefill 4-bit TurboQuant: **49.2 GB**;
- log reports 11/48 cache layers converted;
- exact needle retrieval passed at ~6K and **64,165** tokens.

Crucial negative:
- a second phase that quantized during prefill was implemented/tested;
- it **did not move the practical context ceiling**;
- it was therefore omitted from the PR.

Project-51 interpretation:
- direct Apple QSA TurboQuant integration is no longer hypothetical;
- **do not convert post-prefill GB saved directly into max-context credit**;
- cold-prefill transient, recurrent/GDN state, dense scratch and allocator headroom remain first-class;
- for dual-M1/TB4, TurboQuant earns context credit only after an exact cold admission ladder.

No transfer to Windows Strata's protected-K policy.

## UPDATE — oMLX #3437: streamed experts fit Flash-Next on 64 GB, but the real ceiling is ~121-122K

PR:
https://github.com/jundot/omlx/pull/3437

Older PR updated/rebased in this strict window.

Mechanism:
- mmap/page-backed streaming for ~46.87 GB of routed-expert weights;
- allows Qwen3.8-Flash-Next-MLX-oQ2-MTP to run on a 64-GB M4 Pro where full residency does not fit.

Measured single-request prefill:
- ~40K: **~178 PP**;
- ~76K: **~124 PP**;
- ~96K: **~111 PP**.

The author explicitly walks back the earlier **~200K+** projected context ceiling:
- measured wall: **~121-122K**;
- cause: real chunked-prefill transient memory reaches the hard watermark;
- production config is now **max_context_window 120000**;
- requests near the wall can abort gracefully rather than crash.

This is **not** the Project-51 dual-M1 topology:
- M4 Pro, not M1 Max;
- one 64-GB node, not two 64-GB nodes over TB4;
- oQ2 and oMLX, not the final Project-51 artifact/runtime.

Durable lesson:
- single-node Apple streaming/TQ cannot be used as evidence for a 200K+ ceiling;
- the dual-node target survives, but its capacity proof must include **real cold-prefill transient peaks**, not weight/KV arithmetic alone.

## NEW — TensorFold #287 corrects a false "normal resume re-prefills" interpretation

PR:
https://github.com/ashhart/TensorFold/pull/287

Created **2026-10-02 23:26:27 UTC**.

TensorFold's earlier trial notes had blamed 32K resumed-turn 61-79 s re-prefills on 0.6.2.
The new controlled run shows that was a benchmark artifact:
- the test edited the end of the last user message instead of appending a normal assistant/new-user turn;
- normal multi-turn append on 0.6.2 was already fast (~0.20-0.26 s TTFT at 32K);
- the real gap is a **tail edit**, which has no earlier checkpoint and can force a full re-prefill.

The PR adds one extra checkpoint before the history boundary for long histories:
- 32K tail edit: **60.9 s -> 1.06 s**;
- cost: one additional cached prefix; ~0.8 GiB in the cited 32K GLM case.

Project-51 correction:
- do not cite this specific TensorFold benchmark as evidence that ordinary resumed Mac turns are broken;
- the broader retained-state qualification rule remains because separate >100K retention/admission issues still exist.

No dual-M1 Flash target move.

## UPDATE — TensorFold #210: loop guard remains an opt-in agent-safety mechanism

Older PR updated at the end of this window.

The proposed off-by-default loop guard watches only hidden reasoning and forces a think-close after a persistent
short cycle. Reported overhead is microseconds per committed token versus tens of ms for a model forward pass.

This is conceptually relevant to the user's xhigh agent lane, but it does not prove the exact reported 28K-token loop
case is caught live. Do not substitute a heuristic loop guard for model/runtime quality certification.

## NEW — vLLM #59832: restored servers validate recovered output before opening HTTP

PR:
https://github.com/vllm-project/vllm/pull/59832

Created **2026-10-02 23:59:56 UTC**.

vLLM snapshot restore now rehearses/validates recovered output privately before binding HTTP:
- failed/cancelled recovery is terminal;
- parser/plugin validation precedes engine construction;
- two restore cycles on a small Qwen3 model preserved parameter digests and matched one-token ordinary-reference
  outputs exactly in the reported test.

Separate runtime/model, but the design principle is directly relevant:
**restored state should not become externally serviceable until a deterministic canary passes.**

Add this principle to any future Strata conversation/snapshot-restore qualification if parking is re-enabled.

## UPDATE — vLLM #58439 strengthens file-backed PLE as a viable architecture

Older Qwen3.8-Flash-Next PLE PR updated in-window.

DGX Spark / GB10 result:
- 47.7-GiB FP8 PLE table is read from checkpoint-backed pageable pages instead of a table-sized resident allocation;
- 24-29K TTFT roughly **31.8-32.0 s** versus 33.0-33.5 s for the prior offload-worker reference;
- decode ~199 TG, essentially unchanged;
- greedy output 8/8 identical across cold/warm/fresh starts in the reported validation;
- a BF16-table copy generated bit-identical output to the FP8 table in the cited sequential/determinism probes.

New discussion also shows page-fault scheduling matters: prefetching/overlapping page residency can remove most of the
critical-path PLE loading cost on that unified-memory platform.

No direct Windows/Apple target transfer, but it reinforces the Project-51 FP8-PLE direction.

## NEW — Strata Responses API remains planned, not present

Issue #451 received a new user follow-up in-window naming Codex/Hermes/Pi as desired clients.
The maintainer's existing position is that stateless `/v1/responses` is planned after current fixes.

Project-51 implication:
- do not assume Codex/Pi compatibility through the Responses API today;
- existing OpenAI chat-completions / Anthropic surfaces remain the certification interfaces until this lands.

## Strict-window negatives

Searched:
- Strata;
- oMLX;
- TensorFold;
- llama.cpp;
- SGLang;
- vLLM;
- MLX;
- DASLab / Hugging Face;
- TurboQuant;
- mlx-serve;
- Ishizuki.

Strata main still declares **0.1.37**.
No TurboQuant repository change.
No Ishizuki change.
No target-moving MLX-core change.
No new strict-window DASLab long-agent/xhigh IQ3_S quality table; the live model card remains at IQ3_S 3.50 bpw /
83.6-GB full download with AIME25 100.00, GPQA-D 92.93 and LCBv6 86.86.
No strict-window item justifies changing the primary 5070-Ti TG/PP centers.

## Target state after this pass

1. Primary Strata baseline: **0.1.37**.
2. IQ3_S/native262K physical-fit prior: **~95%**.
3. Windows 16-GB/64-GB admission: **~90%**.
4. 8 h / 24 h zero-stall: **~75% / ~55%**.
5. #481-style automatic containment/no-manual-service-restart: **~85%**.
6. Strata expert-cache release/refill: **OFF** for certification; optional shared-workstation feature later.
7. Conversation parking: **OFF** for initial baseline.
8. High/xhigh: explicit reasoning budget.
9. AA/source runs: fixed residency / adaptive swaps off.
10. PLE ladder: stock IQ4_NL -> FP8 production-fidelity candidate -> BF16 source control.
11. Apple TurboQuant: **working QSA implementation, but no context-ceiling credit without cold-prefill-transient proof**.
12. Single-64GB Apple Flash-Next streaming evidence: ~121-122K ceiling on the cited M4 Pro/oQ2 lane; **not a dual-M1 target**.
13. Dual-M1/TB4 200K+ remains a separate qualification target, not inferred from single-node arithmetic.
14. IQ3_S TG/PP centers: unchanged.
15. Native Windows production context target: **262,144**.
16. No hardware purchase change.

## New hard boundary

**2026-10-03 00:20:49 UTC**
