# Project 51 primary-lane research watch — 2026-09-28 17:39 ET

**Freshness boundary entering this pass:** **2026-09-28 20:02:08 UTC**.  
**User cutoff:** **2026-09-28 21:39:35 UTC**.

## Decision

**No 40-TG / 400-PP speed-target change.**

Two non-speed planning updates:
- the CUDA->Apple handoff is now a formal qualification target, because TensorFold #77 demonstrates a real CUDA-state -> MLX-cache continuation path;
- the Strata IQ3_S **AA>=40 planning prior rises ~75% -> ~80%** after DASLab reports **82.0 SWE-bench Verified vs 82.8 BF16 (~99.0% retained)** on the unpruned IQ3_S build. This is still not a measured Project-51 AA score.

---

## NEW — TensorFold #77 directly validates CUDA prompt-state -> MLX continuation

Issue opened **2026-09-28 21:32:47 UTC**. This is the closest external experiment yet to the Project-51 heterogeneous-prefill design.

Setup:
- Qwen3.8-27B 4-bit, identical checkpoint bytes on both machines;
- CUDA producer: DGX Spark / GB10, TensorFold 0.3.6.2;
- MLX consumer: M3 Ultra;
- producer state serialized to safetensors; consumer loaded it directly into the MLX Qwen3.5-family cache.

State mapping is structurally 1:1:
- CUDA `conv[i] (k-1, conv_dim)` -> MLX `ArraysCache[0]` after adding batch dim;
- CUDA recurrent `rec[i] (Hv,Dv,Dk)` -> MLX `ArraysCache[1]` after adding batch dim;
- CUDA attention `kv[i] (T,kv_heads,head_dim)` -> MLX KV cache after batch dim + T/head transpose.

Measured state size: roughly **64 KiB per prompt token + ~150 MiB fixed**; about **1.9 GiB at 28K**. The issue estimates ~2 s over 10GbE, but transfer was not actually measured over that link, so no transport-latency credit.

### 28,227-token prompt / 64-token greedy continuation

| Producer prefill | PP | Tokens equal to Mac-native prefill | Min cosine K/V | Min cosine recurrent |
|---|---:|---:|---:|---:|
| CUDA fast prefill / FP8 inputs | **1,593** | **40/64** | **0.850** | **0.949** |
| CUDA fast prefill OFF / BF16 inputs | **469** | **55/64** | **0.964** | **0.997** |
| Mac native chunk-plan control | **400** | **33/64** vs another Mac chunk plan | **0.968** | **0.997** |

At **8,925 tokens**, the FP8 CUDA-import continuation matched the Mac's native prefill on all 64 tokens.

Layerwise diagnosis: FP8 K/V drift compounds with depth and prompt position; late-layer K/V is the main problem. BF16 producer state is roughly inside the Mac's own chunk-plan variability envelope.

### P51 consequence

This materially de-risks the bridge architecture:
- **transport/layout is not the hard problem**;
- the hard problem is a **handoff-safe producer precision/execution plan** that retains CUDA's PP advantage without drifting beyond the Mac consumer's own allowed numerical envelope.

TARGETS now defines qualification:
1. 32K first;
2. then 96K / 128K;
3. imported continuation must diverge no earlier than the Mac-native chunk-plan control;
4. needles + agent replay must pass;
5. export only from a committed safe frontier;
6. producer fast-path PP earns no bridge credit if its state drift exceeds consumer tolerance.

For Flash-Next the state schema is more complex than dense27B: P51 still needs QSA/indexer/PLE/MTP-specific state on top of this proven conv/recurrent/KV pattern.

---

## NEW — MLX-Serve #614: approximate prompt-lookup acceptance can make coding agents loop

Merged **2026-09-28 21:32:03 UTC**.

Under `--mtp-typical`, prompt-lookup drafts reused the typical-acceptance rule designed for MTP distributions. But a lookup draft is a **point mass copied from context**. A merely plausible copied token could therefore become deterministic: at entropy H=2 and threshold 0.2, target probability ~3% already clears the typical floor.

Observed agent regression:
- pre-lookup baseline: **0/4** loop stops;
- v26.9.6-derived builds: **11/19** agent runs loop-stopped in prior observations.

Controlled 12-sample arms:
- lookup + typical: **2/12 loop-stops**, worst distinct-8 = 0.653;
- lookup off + typical: 0/12;
- lookup + exact: 0/12;
- lookup off + exact: 0/12;
- lookup + typical with this fix: **0/12**, worst distinct-8 = 0.947.

Copy-heavy rewrite performance was essentially unchanged by exact lookup acceptance: sampled **240.2 -> 239.1 TG**, with ~85-87% lookup landed.

### P51 consequence

**Acceptance semantics are draft-source-specific.** MTP, prompt lookup/copy, n-gram, tree and other proposal sources must each use an acceptance rule mathematically valid for that proposal distribution. A single 'typical' shortcut cannot be globally reused.

Add agent-loop / n-gram-diversity checks to verifier certification, not just drafted==serial under greedy.

---

## NEW — vLLM #58784: never verify speculative slots that were never proposed

Merged **2026-09-28 20:07:16 UTC**.

On a P/D resume, placeholder draft slots were left as zeros in MRV2 and then verified as real token-0 proposals. With probabilistic/block verification, all placeholders could be accepted.

Physical failure mode: **71/80** MT-Bench responses through the affected 1P1D path began with at least eight NUL tokens. After the fix: **0/80**; greedy outputs remained 80/80 identical.

### P51 consequence

Every verify row needs an explicit validity/proposal mask. Unproposed/padded rows must be impossible to accept, even if their backing tensor contains a syntactically valid token id.

---

## NEW — vLLM #57107: dynamic acceptance-estimator shapes can trigger runtime compilation stalls

Merged **2026-09-28 20:46:27 UTC**.

Triton scalar specialization created many compiled variants as `num_reqs` / `num_tokens` crossed values such as 1 and multiples of 16. Disabling those specializations collapsed:
- accumulate kernel **14 variants -> 1**;
- local-max/sumexp **3 -> 1**;
- predict **3 -> 1**.

### P51 consequence

For Apple verifier kernels, shape specialization should be intentional and bounded. Verify-width/concurrency routing may select from a small frozen kernel family, but incidental scalar values must not create compile/cache churn during serving.

---

## NEW — TensorFold #76 M1 agent-loop triage points away from a proven runtime defect

Physical M1 Max 64GB / Qwen3.8-27B + DFlash2 / TensorFold 0.3.6.2 no-thinking agent repeatedly wrote near-identical successful reproduction tests rather than making the code fix. A short MTPLX run showed a similar repeated-search pattern, so TensorFold was not isolated as cause.

Same-window bounded follow-up changed only `--no-thinking` -> `--thinking` (plus unavoidable CI overlap):
- agent moved from reproduction to controller edit;
- added regression tests;
- finished in **13 model turns**;
- **4/4 independent verifier checks passed**, reward 1.0;
- no server errors, swap growth or memory-pressure failure.

### P51 consequence

Keep this as an **agent-policy/configuration watch**, not a TensorFold defect. AA-agent certification should test thinking/no-thinking and recommended sampling separately; a no-progress guard belongs in the orchestrator even when the runtime is correct.

---

## NEW — Strata #90 is an agent context-budget integration issue, not evidence of context corruption

RTX3090 / Strata0.1.20 / IQ3_XXS / Hermes reports **50-60 TG**, then gets:
`prompt 70,527 + max_tokens 65,536 > context 131,072`.

The arithmetic is valid: Strata reserves the requested output allowance and explicitly does not truncate. The client/session needs a smaller dynamic output cap or earlier compaction.

### P51 consequence

Agent orchestration must budget **prompt + reserved output <= resident context window**. The runtime should expose remaining-context headroom so the client can set a realistic per-turn output cap instead of reserving a fixed 64K late in a long session.

No performance-target credit from the 50-60-TG anecdote because hardware/config/context details are insufficient for a controlled receipt.

---

## RECOVERED CURRENT — DASLab IQ3_S SWE-bench Verified is near-BF16

DASLab reports the unpruned Flash-Next GSQ-RCO IQ3_S at **82.0% SWE-bench Verified vs 82.8% BF16**, ~99.0% retained. Their model card also reports IQ3_S AIME25 100.0, GPQA-D 92.93 and LCBv6 86.86, task average 93.26 vs BF16 93.12.

This result predates the strict boundary and is therefore **RECOVERED CURRENT**, not NEW.

### P51 consequence

Raise only the **IQ3_S AA>=40 planning prior ~75% -> ~80%**. Do not call it AA-certified: custom P51 still needs xhigh tools, long-context semantics, state continuity, thinking behavior and speculative-acceptance checks.

IQ3_XXS quality priors remain unchanged.

---

## STRICT-WINDOW non-events

- **Strata:** no 0.1.21 release, no new exact-5070Ti TG/PP ladder, no longer exact-card soak.
- **TensorFold:** no new commit after 0.3.6.2; #77 is proposal/measurement, not merged support.
- **oMLX:** no new issue/commit opened in-window.
- **Ishizuki / MTPLX / DFlash / Splash / llama.cpp:** no primary-lane performance commit in-window.

---

## Canonical planning effect

**40/400 unchanged.**

The bridge is now substantially less speculative: a Qwen3.8 hybrid CUDA state has been physically imported into MLX and continued successfully. Project 51's remaining bridge uncertainty is concentrated in **producer numerical fidelity, Flash-specific state completeness, committed-frontier ownership, transfer time, and 96K/128K validation** rather than basic tensor-layout compatibility.

## New hard boundary

**2026-09-28 21:39:35 UTC**
