# Project 51 research watch — 2026-09-23 03:55 ET

**Freshness boundary:** consolidates the Project 51 research deltas discussed after the prior canonical cutoff **2026-09-22 15:59:04 UTC**, through approximately **2026-09-23 07:55 UTC**.

## Decision

This pass makes three durable changes:

1. **Production quant identity is now xhigh-specialized, not universal-medium/xhigh.** The user's intended local operating mode is xhigh. The optimization target is therefore the cheapest Apple execution representation that remains source-like at xhigh/agent use, rather than a quant that must preserve every reasoning-effort distribution equally.
2. **PP2 feasibility confidence increases materially.** Qwen4-Exp / Flash-Next PP2 is now demonstrated across two physical nodes with correctness checks and a documented mHC boundary contract. This does not prove M1/TB4 throughput, but it substantially reduces architectural feasibility risk.
3. **The path from ~mid-20s target decode to ~40 TG is now mechanistically better defined.** Current Flash-Next MTP verification has a measured ~2.3x target-forward cost on Apple; the identified GDN + MoE verify overheads are large enough that reducing verify toward ~1.5x would plausibly produce the ~1.5-1.7x effective uplift P51 needs.

Canonical headline targets remain **40 TG @ ~128K**, **400 cold PP**, with **~70% planning confidence for >=40 TG**. The quality objective is strengthened to **source-like ~AA40-class behavior at xhigh**; >=38 remains a rejection floor, not the desired production endpoint.

---

## NEW — xhigh-specialized production quant policy

Source/prior:
- ISTA-DASLab Qwen3.8-Flash-Next GSQ/RCO release and discussion on reasoning-effort sensitivity.
- Project 51 user workload policy: local Flash-Next will be driven at **xhigh**, not medium.

The DASLab 3.00-bpw Flash allocation remains unusually strong xhigh evidence: its calibration traces and published reasoning benchmarks were generated at xhigh, while community medium-effort tests show materially larger degradation. For a universal-serving artifact this is a limitation. For P51's actual production distribution, it is specialization toward the intended workload.

### P51 consequence

Do **not** spend bandwidth merely to preserve medium reasoning if medium is not a production mode.

Current search policy:

- start near **~3.5 average transformer BPW**;
- explicitly test approximately **3.0 -> 3.2 -> 3.4 -> 3.6** heterogeneous allocation arms;
- preserve high precision in QSA/indexer, recurrent/GDN-sensitive tensors, norms, router/shared experts, output/head and MTP-sensitive paths;
- push the routed-expert bank hardest;
- promote the lowest-cost arm that is statistically source-like on repeated xhigh coding, hard reasoning, tool use, long-context retrieval and multi-turn agent trajectories.

Current engineering estimate for the likely source-like xhigh frontier is **~3.3-3.6 average transformer BPW**, with ~3.4-3.5 as the center hypothesis. This is **not measured AA certification**.

Medium-effort cross-tests remain useful diagnostics for calibration-domain overfitting, but they are no longer a production admission requirement for the xhigh-only artifact.

---

## NEW — SiliconSpecies Swift/Splash audit

Source:
https://huggingface.co/SiliconSpecies/Swift-Qwen3.8-27B-Splash

### Supported

- reverse-engineered Splash package representation is operational and includes concrete format discoveries;
- most BF16 norm tensors use a stored `gamma + 1` convention, with GDN norm as an exception;
- controlled M5 Max prompt-length sweep includes cache salting to avoid false prefill wins;
- 64K result reports **87.8 TG Splash vs 36.6 TG oMLX** for the tested system configurations.

### Qualification

The 64K ratio is a valid end-to-end configuration comparison, **not** a clean kernel-only 2.4x result: the target representations and speculative behavior differ.

The published 95/95 quality suite is saturated and therefore useful as a catastrophic-conversion guard, not evidence of source-level intelligence retention.

The stronger durable lesson is the format/correctness trap: local reconstruction or isolated kernel tests can pass while a small semantic mismatch destroys multi-step reasoning.

### P51 consequence

Keep **real-model greedy/logit/agent parity above isolated kernel-unit correctness**. Package/quant conversion validation must include actual model behavior, especially for small high-leverage tensors.

---

## NEW — EXL3 / trellis audit

Sources:
- https://github.com/turboderp-org/exllamav3/blob/master/doc/convert.md
- https://github.com/turboderp-org/exllamav3/blob/master/sc_optimize.py
- https://github.com/beamivalice/PonyExl3/blob/master/README.md

EXL3 is materially more interesting than a uniform "N bpw" hardware map implies. Current conversion supports higher-bit heads, separate MTP / n-gram precision, HQ promotion of sensitive structures, and arbitrary per-tensor recipes. The optimizer uses sensitivity/logit-divergence information to allocate rate.

### P51 consequence

Treat EXL3 as a **heterogeneous-allocation/runtime challenger**, not as evidence that a low nominal BPW has a universal quality equivalence.

Teacher-logit / KLD proximity remains an allocator signal, not an AA/agent-intelligence certificate.

PonyExl3 proves the trellis representation can be executed from compressed form in Metal, but current M1 dense-27B performance does not displace the Apple7/Splash/oMLX production path. Keep EXL3/Pony as a research branch.

---

## NEW / MERGED — oMLX #3520 gathered-QSA long-context path

Source:
https://github.com/jundot/omlx/pull/3520

The merged PR removed a major long-context decode pathology: gathered QSA previously transposed / reshaped the whole KV cache before selecting the small sparse subset. On M5 Max, per-QSA-layer gather cost at 206K fell from **1.83 ms** to **0.27 ms**.

Reported serial decode improvements vs prior main:

- 63K: **+7.5%**
- 134K: **+18%**
- 229K: **+28%**

With adaptive MTP under production sampling:

- 63K: **+8.5%**
- 134K: **+25%**
- 229K: **+36%**

The implementation also demonstrates a width-sensitive policy: very small query/verify widths prefer stored-layout gathers, while larger prefill widths can prefer copy-once / flat-gather below a context threshold.

### P51 consequence

This directly supports:

- no whole-cache transformation on token decode;
- gathered sparse-QSA verification;
- **width-sensitive verify/prefill kernel dispatch** rather than one universal path.

Do not numerically transfer M5 gains to M1, but prioritize the same structural optimization.

---

## RECOVERED / PROMOTED — measured MTP verify economics, oMLX #3374

Source:
https://github.com/jundot/omlx/issues/3374

Measured on Qwen4-Exp / Flash-Next, M3 Ultra, depth-5:

- base forward: **1.0x**
- GDN sequential recurrence: **~+0.5x**
- MoE expert union: **~+0.6x**
- QSA indexer: **~+0.2x**
- total verify cost: **~2.3x one target forward**

At that cost:
- prose ~2.4 accepted tok/cycle => ~**1.04x** effective;
- tool calling ~3.1 => ~**1.35x**.

Proposed/estimated improvements:
- expert-union dedup: save ~0.3x;
- chunked/TreeWY-style GDN verify: save ~0.5x;
- combined verify target: **~1.5x**.

The 2.3x decomposition is measured. The 1.5x outcome is a hypothesis / implementation target.

### P51 consequence

The P51 40-TG thesis should be expressed as a verifier-economics problem, not a generic "MTP multiplier":

> target execution in the mid-20s TG + verify cost reduced enough to realize ~1.5-1.7x useful-token uplift.

Prioritize MoE union dedup and parallel/chunked GDN verification after gathered-QSA.

---

## NEW — SGLang Qwen4-Exp PP2 proof, #39393

Source:
https://github.com/sgl-project/sglang/issues/39393

A production-like local patch runs Flash-Next / Qwen4-Exp with **PP2 across two physical 8x4090 nodes**, no NVLink/P2P across nodes, under a 160-request replay. Temperature-0 correctness passes.

Key mechanism evidence:

- TP16 cross-node AllReduce: ~**17 ms/layer** in the reported setup;
- PP2 stage-boundary transfer: **<0.4 ms per request window**;
- PP2 avoids repeated cross-node layer collectives.

Important model-specific contract:
- HyperConnection / mHC PP boundary carries the already-wide `hidden_states` representation;
- copying a normal Qwen3-style `{hidden_states, residual}` contract is incorrect.

Important warning:
- PP2 + CUDA graph was correct in the report;
- an eager PP path could silently corrupt output after several generated tokens.

### P51 consequence

PP2 is now demonstrated on the exact architecture family. Increase architectural feasibility confidence, but do **not** transfer NVIDIA throughput to M1.

Stage ownership remains mandatory:
- embeddings only where needed;
- each stage owns its GDN/QSA/KV/MTP state;
- TB4 carries stage-boundary activations, not expert weights or chatty collectives.

---

## NEW — dynamic expert residency evidence, SGLang #37792

Source:
https://github.com/sgl-project/sglang/issues/37792

A 2.572-bpw Flash-Next build on a 24-GB Blackwell GPU + 32-GB host RAM demonstrates tiered expert residency.

At the minimum resident cache:
- **184 / 512 experts per layer resident**
- those experts cover **84.3% of routing mass**
- expert traffic drops from **26 GB/token -> 0.31 GB/token**
- same-machine optimization ladder reaches the mid-50s TG at ~10K context.

This is capacity/runtime evidence, not quality evidence and not M1 transfer.

### P51 consequence

Promote **stage-local dynamic expert residency** from optional future capacity trick to an architecture feature worth preserving from day one.

Even if 2x64 GB can fully hold the chosen production quant, hot-expert locality may still reduce cache/memory pressure and becomes highly relevant to future Qwen4 / larger sparse models.

Never fetch experts across TB4; misses must be serviced from the owning stage's local hierarchy.

---

## NEW — thin-link Flash-Next systems evidence: flashnext-hybrid

Source:
https://github.com/ucicelos/flashnext-hybrid/blob/main/README.md

Cross-hardware system: large-memory AMD APU + RTX 3090 Ti eGPU over a thin PCIe link.

Key lessons are architectural rather than numeric:

- placement/state/rollback mistakes can dominate;
- sparse attention can accidentally pay dense-context bandwidth;
- speculative batches can fragment into singleton target work;
- **~90% draft acceptance can still make throughput worse** if verification destroys batching;
- forcing common verification width can lower nominal acceptance while increasing aggregate TG.

### P51 consequence

Optimize **accepted useful tokens per expensive target verification batch**, not raw acceptance percentage.

This independently supports P51's planned multi-row PP2 verifier:
- keep verification width scheduler-visible;
- batch rows even when some low-confidence drafts are likely to reject;
- pipeline those verify batches across PP stages.

---

## UPDATE — oMLX #3771 remains a correctness/performance warning

Source:
https://github.com/jundot/omlx/issues/3771

Flash-Next dev4 failed to engage fused GDN verify prework on all 36 GDN layers because fast-path eligibility relied on exact method identity rather than semantic capability.

Measured M5 Max code:
- older working path: **96.4 TG**
- dev4 + separate transaction fix: **77.4**
- restoring fused prework gate: **81.1**

### P51 consequence

Public runtime numbers are not mature ceilings. Instrument fast-path engagement separately for target, draft and verify.

Compatibility gates should express numerical contracts, not exact class/method identity.

---

## UPDATE — M5 Ultra is a reference ceiling, not a P51 transfer

Reference:
https://www.macstories.net/stories/m5-ultra-mac-studio-review-the-dream-mac-for-local-ai-agents/

Current M5 Ultra 256-GB oMLX/Flash-Next measurements show genuinely filled long-context decode remaining strong and cold prefill in the multi-thousand tok/s range.

### P51 consequence

Use M5 Ultra as a **single-node reference / upper-bound environment** only. Do not numerically transfer its rates to Apple7.

Its existence strengthens the view that Flash-Next long-context architecture itself is not the limiting problem; P51's challenge is extracting comparable software efficiency from much older M1 silicon.

---

## UPDATE — Qwen4 relevance

Sources:
- https://github.com/QwenLM/Qwen3.8-Flash-Next
- official Alibaba Qwen4 roadmap announcements

Flash-Next is explicitly presented as an early preview of the architecture used in Qwen4. Qwen4 is reported as in training; no reliable public total/active-parameter or local-inference requirement exists yet.

### P51 consequence

Preserve generality in:
- stage-local sparse expert residency;
- QSA/recurrent state ownership;
- external PLE/lookup placement;
- heterogeneous quant allocation;
- PP2 activation-only transport.

These are likely to transfer to the next architecture generation better than model-specific whole-file quant assumptions.

---

## Canonical planning state after this true-up

### Quality / quant

- Production use mode: **xhigh**.
- Desired quality: **source-like ~AA40-class behavior at xhigh**.
- >=38 remains a hard reject floor, not the production goal.
- Current search band: **~3.0-3.6 experimental**, with **~3.3-3.6** the current likely source-like xhigh region and ~3.5 the recommended first serious candidate.
- Whole-file BPW remains non-authoritative; PLE and MTP precision are tracked separately.

### Dual-M1 Flash

- PP2 remains primary; TP2 is a falsification/control benchmark.
- 40 TG @ ~128K: **~70% planning confidence**.
- 400 cold PP remains the working target.
- 50/500 remains stretch/headline territory, not promoted expectation.

### Implementation priority

1. xhigh-source-like heterogeneous quant qualification;
2. exact PP2 stage ownership / mHC boundary semantics;
3. gathered QSA for decode and verify;
4. MoE expert-union dedup;
5. chunked / parallel GDN verification;
6. width-sensitive verify dispatch;
7. PP2 pipeline overlap across verification batches;
8. stage-local hot-expert residency;
9. real-model greedy/logit/tool/agent parity after every optimization.

## New hard boundary

**2026-09-23 ~07:55 UTC**
