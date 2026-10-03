# Project 51 research watch — 2026-10-02 23:26 ET

Freshness boundary entering: **2026-10-03 00:20:49 UTC**
Cutoff: **2026-10-03 03:26:54 UTC**

## Decision

This pass makes **three durable planning changes** but **no numeric primary-Windows fit/stability target movement**.

1. **Strata 0.1.38 is the current primary baseline.**
   The release commit predates the entering boundary and was missed by the prior pass, so this is a
   **RECOVERED OLDER EVIDENCE** correction, not a strict-window release event.

2. **The single-M1 Qwen3.8-27B lane is promoted from “runtime comparison” to an explicit custom-engine experiment.**
   Recovered MTPLX evidence shows a concrete pre-M5 long-context verifier inefficiency: the packed-GQA verify lane
   fails to dispatch, causing context-dependent verify cost to scale with draft depth. The reporter estimates
   **~+30% at 64K and ~+39% at 88K** if the one-sweep verify path is restored. That estimate is not an M1 measurement
   and does not move the 25-TG working target, but it identifies a high-value kernel seam for our own M1 engine.

3. **RX 6800 becomes a formal prefill-producer experiment for the dense-27B lane, not merely a background-agent node.**
   RDNA2/gfx1030 now has stronger evidence: Strata documents ~330-339 PP on an RX 6900 XT-class card for Flash-Next,
   the maintainer reports an exact RX 6800 improving to ~42 TG on Windows 0.1.37, and llama.cpp has a dual
   RX6800/6800XT Qwen3.8-27B Q4_K_M receipt around **230 PP on a fresh 15K prompt**. There is still no clean
   single-RX6800 + DASLab/ByteShape 27B prefill receipt, and HIP->Apple continuation-state import is unimplemented.
   Treat this as an experiment, not PP credit.

Current primary Windows state remains:
- Strata baseline: **0.1.38**;
- IQ3_S/native262K physical fit/admission: **~95%**;
- Windows 16-GB/64-GB full-context admission: **~90%**;
- 8 h / 24 h zero-stall: **~75% / ~55%**;
- #481-style automatic containment/no-manual-service-restart: **~85%**;
- conversation parking OFF for the initial production baseline;
- explicit `reasoning_budget_tokens` for high/xhigh;
- frozen expert residency for source/AA qualification.

## RECOVERED OLDER EVIDENCE — Strata 0.1.38 is already released

Release commit:
https://github.com/Niko1221/Strata/commit/5123c976d3aa98563651ecf602aede63281e4618

Created **2026-10-02 20:54:11 UTC**, before the entering hard boundary.

Main now declares:
- `project(strata VERSION 0.1.38 ...)`;
- setup minimum engine 0.1.38.

0.1.38's release batch includes:
- grouped prompt expert gather (#372);
- first-chunk PLE overlap with layer 0 (#374);
- bitwise DeltaNet three-head recurrence kernel (#413);
- q4_0 QSA prompt attention on tensor cores (#452);
- Q5_0 experts on GPU (#473);
- IQ4_XS AVX2 expert path (#415);
- unbuffered Windows expert/file loading (#357/#362);
- opt-in peer-device expert-cache tier (#531);
- low-VRAM/startup fixes.

These are favorable performance/maturity changes, but no new exact 5070-Ti/IQ3_S/native262K controlled ladder in
this pass justifies moving the canonical TG/PP centers or fit priors.

Important: open agent-surface fixes below are **not** part of the 0.1.38 release merely because they target 0.1.38.

## NEW — Strata #572 fixes silent loss of unfinished current tool calls

PR:
https://github.com/Niko1221/Strata/pull/572

Created **2026-10-03 02:13:26 UTC**, open.

On v0.1.38, if generation ends after announcing a tool call but before completing it, current Chat Completions and
Messages parsing can return:
- empty content;
- no tool call;
- clean stop semantics.

The PR returns the raw unfinished call text as content instead of silently discarding it; complete-call parsing remains
unchanged in the reported tests.

Project-51 consequence:
- #572 joins #510/#525/#537 in the required autonomous-agent parser gate;
- do not call 0.1.38 “agent parser fixed” yet.

## NEW — Strata #571 adds an experimental Responses API, still open

PR:
https://github.com/Niko1221/Strata/pull/571

Created **2026-10-03 02:03:24 UTC**, open.

Opt-in `/v1/responses` support adds:
- create/retrieve/delete and input-item pagination;
- `previous_response_id` continuations;
- client-owned function-call/result loops;
- typed streaming text/argument deltas.

Explicitly out of scope in the PR:
- background execution/cancel endpoint;
- image input;
- reasoning representations;
- hosted tools;
- compaction;
- WebSockets.

This is useful for future Codex/Pi compatibility, but Project 51 continues to certify existing Chat Completions /
Anthropic surfaces until this PR ships and the parser gates pass.

## NEW — Strata #567 removes repeated full-history CPU tokenization cost

PR:
https://github.com/Niko1221/Strata/pull/567

Created **2026-10-03 01:54:47 UTC**, open.

Instead of BPE-tokenizing the entire rendered conversation every turn, the server reuses token ids through the last
safe shared special-token boundary.

Synthetic ~100,893-token conversation:
- full encode median: **235 ms**;
- incremental encoder: **1.5 ms**;
- tests/fuzz claim identical token ids.

This is a useful long-agent latency cleanup, but it is CPU/tokenizer overhead, not model PP. Do not fold it into cold
PP targets.

## RECOVERED OLDER EVIDENCE — MTPLX pre-M5 27B verify path leaves major long-context headroom

Issue:
https://github.com/youssofal/MTPLX/issues/506

Created 2026-09-18; still open. Recovered because the user explicitly reopened the single-M1 27B engine lane.

Environment in the report:
- M3 Max 128 GB;
- Qwen3.8-27B Optimized-Speed;
- MTPLX 2.11.3/2.12.0;
- pre-M5 packed-GQA verifier path.

Measured production telemetry:
- 4-16K: ~32.9 TG;
- 16-32K: ~27.5;
- 32-48K: ~23.8;
- 64K+: ~20.2.

The report finds:
- context-dependent verify traffic scales strongly with MTP depth;
- the packed-GQA verify kernel intended for q=2..4 over long dense KV reports only bails;
- the paged route reports zero calls;
- acceptance remains roughly flat, so most throughput decay is cycle-time growth rather than worse drafting.

Reporter's **estimated**, not measured, fix effect:
- ~64K: ~29 -> **~38 TG** (+30%);
- ~88K: ~23.5 -> **~33 TG** (+39%).

The maintainer later confirmed the issue is scoped to **M1-M4** because M5 uses the NAX flash route; the root routing
problem remains open.

Project-51 consequence:
- our custom M1 27B engine should explicitly implement/benchmark **one KV sweep per multi-row verify window**;
- verify path must be shape-stable at q=2..4 (and our desired wider rows), not silently fall to per-position attention;
- measure 16/32/64/96/128K, not only short-context MTP speed;
- no numeric 25-TG target move yet because the published fix uplift is an estimate on M3, not a physical M1 result.

### Recovered clarification — MTPLX 2.11.1 semantic corruption is fixed, not a standing indictment

MTPLX issues #459/#464 reported severe Qwen3.8-27B MTP semantic corruption on M1-M4 above the 8K route threshold.
The maintainer traced it to an M5 tensor-unit NAX path accidentally enabled on older Apple GPUs and fixed the hardware
gate in **2.11.2**.

Therefore do **not** count those old reports as evidence that Qwen3.8-27B MTP is intrinsically unstable on M1.
The still-open long-context inefficiency is #506, not the already-fixed NAX misdispatch.

## NEW — MTPLX #583 shows the same unclosed-reasoning agent class on another runtime

Issue:
https://github.com/youssofal/MTPLX/issues/583

Created **2026-10-03 00:36:25 UTC**.

MTPLX 2.12.0 can return empty visible content after a tool result when:
- tools are declared;
- the model answers inside the template-opened think block;
- it omits `</think>`.

The report reproduces 2/6 failures repeatedly on both OpenAI and Anthropic protocol paths.

This independently confirms that reasoning/tool boundary handling is a **runtime-parser problem class**, not unique to
Strata. Our own M1 engine/server must design this parser state machine explicitly and test it with agent traces.

## UPDATE — RX 6800 / RDNA2 support is stronger than the previous secondary-lane description

Strata issue:
https://github.com/Niko1221/Strata/issues/539

The maintainer now states gfx1030/RDNA2 is supported:
- Linux: HIP source build;
- Windows: ready-made HIP engine includes gfx1030;
- RX 6900 XT community run: 38-42 TG;
- **RX 6800 Windows run: ~31 -> ~42 TG on 0.1.37** after runtime improvements.

Current Strata AMD docs provide the detailed same-architecture RX 6900 XT / 63-GB host receipt:
- Swift 1.5 IQ3_XXS, 131,072 context;
- **38-42 TG** at full context;
- **246 PP** around 2K;
- **330-339 PP** with auto 8K chunks;
- no hipBLASLt on gfx1030; plain hipBLAS is the dense-prefill path.

That is direct evidence that gfx1030 can be a respectable prefill machine, though it is Flash-Next and RX6900 rather
than the user's exact RX6800/dense-27B configuration.

## RECOVERED OLDER EVIDENCE — dense 27B runs on RX6800-class ROCm hardware

llama.cpp discussion #27954:
https://github.com/ggml-org/llama.cpp/discussions/27954

Dual RX 6800 XT + RX 6800, Qwen3.8-27B Q4_K_M, ROCm:
- 65K configured context;
- fresh ~15K prompt: **~230 PP**;
- decode ~18.5-19.4 TG;
- MTP depth-2 only modestly improves decode in that setup.

This is a poor topology for our intended appliance because the model is layer-split across two cards.
However it proves the dense Qwen3.8-27B family runs on gfx1030 and gives a real PP scale.

For Project 51's **single RX6800 16-GB** prefill-producer experiment:
- prefer DASLab IQ3_S / IQ3_XXS or ByteShape ~3.2-3.8-bpw candidates that fit wholly inside 16 GB;
- first measure cold 16/32/64/96/128K PP locally;
- do not assign a production PP target from the dual-card Q4_K_M result.

## RECOVERED OLDER EVIDENCE — CUDA->Apple state handoff is structurally feasible; transport has now been demonstrated on a smaller model

TensorFold issue #77:
https://github.com/ashhart/TensorFold/issues/77

Qwen3.8-27B state mapping:
- CUDA `conv` -> MLX ArraysCache conv with batch dimension;
- CUDA `rec` -> MLX recurrent state with batch dimension;
- CUDA `kv` -> MLX KVCache with batch dimension + T/head axis swap.

At 28,227 tokens:
- exported state ~1.9 GiB;
- CUDA BF16-input prefill: ~469 PP;
- Mac prefill: ~400 PP;
- imported BF16 state matches Mac-native continuation for 55/64 greedy tokens, while Mac 2K-vs-4K chunk plans
  match only 33/64 in that experiment;
- faster FP8-input CUDA prefill ~1,593 PP drifted more deeply.

The issue was closed because the maintainer chose to carry heterogeneous handoff in **MCDMA**, not because the mapping
was rejected.

MCDMA has since demonstrated an end-to-end **Qwen3-4B** Spark-prefill -> Mac-decode handoff:
- 15,402-token prompt;
- ~2,166 MiB cache transfer in ~0.48 s at ~37.7 Gbit/s;
- split request beat each machine alone in the reported test.

Project-51 interpretation:
- cross-engine state handoff is no longer a purely theoretical architecture;
- **RX/HIP -> M1 is still unimplemented and unproven**;
- any RX prefill appliance must export a committed state with the same semantic contract and pass Mac-native
  continuation equivalence before receiving latency credit.

## DASLab / ByteShape check

No new strict-window DASLab/ByteShape M1 Max receipt was found.

DASLab's current Qwen3.8-27B model card remains:
- IQ3_S: **3.50 bpw / 11.8 GB**, AIME25 100, GPQA-D 89.39, LCBv6 85.71;
- IQ3_XXS: **3.00 bpw / 10.1 GB**, AIME25 100, GPQA-D 88.89, LCBv6 84.57.

These remain the highest-priority low-byte candidates for our own M1 decode engine and the single-RX6800 prefill test.
ByteShape remains a second candidate family; no new exact-M1 receipt changed its rank in this pass.

## Strict-window negatives

Searched:
- Strata;
- oMLX;
- TensorFold;
- Ishizuki;
- MTPLX;
- Splash M1 port;
- llama.cpp;
- SGLang;
- vLLM;
- MLX;
- TurboQuant;
- mlx-serve;
- DASLab/Hugging Face;
- ByteShape/public sources.

No TurboQuant repository change.
No Ishizuki strict-window change.
No Splash-M1 strict-window change.
No target-moving MLX-core change.
No strict-window DASLab/ByteShape long-agent quality table or exact M1 Max benchmark.

## Target state after this pass

1. Primary Windows Strata baseline: **0.1.38**.
2. IQ3_S/native262K physical-fit prior: **~95%**.
3. Windows 16-GB/64-GB admission: **~90%**.
4. 8 h / 24 h zero-stall: **~75% / ~55%**.
5. #481-style automatic containment/no-manual-service-restart: **~85%**.
6. Agent parser gate still open: #510/#525/#537/#572; 0.1.38 does not close it.
7. Single-M1 Qwen3.8-27B working target stays **25 TG / 110 cold PP**, but **custom engine becomes an explicit priority experiment**.
8. Custom M1 27B engine must make long-context multi-row GQA verification a first-class kernel, with one KV sweep per
   verify block and a 16K->128K context ladder.
9. Candidate quant order for that engine: **DASLab IQ3_S**, ByteShape ~3.8-bpw quality arm, DASLab IQ3_XXS /
   ByteShape ~3.2-bpw speed-quality arm.
10. RX 6800 secondary lane now includes a **dense-27B prefill-producer experiment**.
11. RX->M1 handoff earns no target credit until HIP state export/import + continuation-equivalence + transfer-cost
    measurements exist.
12. Primary Windows native production context remains **262,144**.
13. No hardware purchase change.

## New hard boundary

**2026-10-03 03:26:54 UTC**
