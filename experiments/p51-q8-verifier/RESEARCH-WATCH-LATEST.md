# Project 51 primary-lane research watch — 2026-09-28 06:51 ET

**Freshness boundary entering this pass:** **2026-09-28 08:53:55 UTC**.  
**User cutoff:** **2026-09-28 10:51:31 UTC**.

Strict boundary preserved. Material that existed just before the previous boundary but was missed is labeled **RECOVERED CURRENT**.

## Decision

**No canonical target change.**

Keep:
- dual-M1 Flash-Next: **40 TG sustained at genuinely filled ~128K**
- dual-M1 Flash-Next: **400 realistic cold PP**
- planning confidence for >=40 TG: **~70%**
- single-M1 dense 27B: **25 TG canonical / ~110 native cold PP**
- 5070 Ti + Strata: experimental Flash lane; 0.1.14 is a promising liveness fix but still needs exact-card soak validation

---

## NEW — TensorFold 0.3.6 ships source-identical SSD expert streaming for Flash-Next

Release commit 85653c77166552722368e0f2466ee8571a8586d9 at **2026-09-28 08:56:58 UTC**; release published 09:23:45 UTC.

New low-memory modes:
- `--ple-on-ssd`: PLE/ngram tables stay on SSD; on an emulated 128-GB budget on M3 Ultra, Flash-Next peaks at **85.6 GiB** and decodes at **0.91–1.03x** the 256-GB resident run.
- `--ssd-experts GIB`: routed experts stream from the checkpoint into a GPU pool. Under an emulated 64-GB budget on M3 Ultra, Flash-Next peaks at **39.5 GiB** and keeps **tokens identical to the resident model**, but decode runs only **0.31–0.39x resident speed**.

These measurements are M3 Ultra under emulated memory budgets, **not M1**.

### P51 consequence

This is strong **capacity/fallback evidence** for a 64-GB Apple node:
- source-identical expert streaming is possible without Cache-Prior-style routing bias;
- PLE SSD offload can be nearly decode-neutral on a large Mac;
- full expert streaming is far too costly to count toward the canonical 40-TG lane unless future M1 measurements surprise us.

For dual-M1, prefer partitioning/hot-resident expert strategies that avoid full SSD expert streaming. Keep TensorFold SSD streaming as a fail-safe capacity lane and a correctness reference.

---

## NEW — TensorFold 0.3.6 exposes an M1–M4 prompt-boundary exactness caveat

The 0.3.6 release explicitly states that on **M1 through M4 with MLX 0.32.2**, Qwen3.8-27B prompt attention around **8,192 keys** does not match one stock MLX call bit-for-bit when a prompt chunk splits with a short tail.

Within one server:
- drafted replies still equal serial replies;
- resumed prompts still equal fresh prompts.

But replies to prompts longer than one prompt chunk can differ between machines with different memory because adaptive chunk size follows each machine's memory budget.

### P51 consequence

Do not use 'drafted == serial' alone as the PP correctness oracle. Our frozen AA/PP harness must:
- pin the chunk plan when comparing machines/runtimes;
- test 8K boundary -1 / exact / +1 and short-tail cases on M1;
- distinguish **self-consistency** from **stock-MLX/source-path identity**.

For dual-M1 PP2, both nodes must derive the same chunk/state boundary policy or carry the chosen plan explicitly in the state lineage.

---

## NEW — TensorFold agent parser can drop a valid tool call inside an unclosed think block

Issue #60 opened **2026-09-28 09:09:14 UTC** on M3 Ultra / Qwen3.8-Flash-Next 4-bit MTP.

Reported behavior:
- model emits a complete tool-call markup before `</think>`;
- parser only splits reasoning at a closing think tag;
- the tool call therefore remains inside `reasoning_content`;
- API returns empty content, no tool call, finish_reason=stop.

Reporter observed **2 of 128 real agent-trace replays** across 20K–250K prompts / 9 tools.

This is a serving/parser defect, not evidence of model-quality loss.

### P51 consequence

Add an **agent protocol gate** to the AA suite:
- tool call inside closed think
- tool call inside unclosed think
- tool call immediately after reasoning budget ends
- streamed/non-streamed tool parsing
- malformed-but-complete XML recovery

AA~40 should include end-to-end tool success, not just token-level model quality.

---

## NEW — Strata 0.1.14 root-causes the residual IQ-model wedge to a host CUDA driver lock

Core change e6265c7195ddc02a708c03d85d8bb317d463bc65 at **09:02:44 UTC**; engine 0.1.14 commit 4d4014cec7060fc4ba329ac3631af23e31fcc6e0 at **09:21:01 UTC**; release published **10:02:48 UTC**.

The 0.1.13 Windows thread dumps finally localized the remaining stall:
- host thread blocked inside **cudaMemcpyAsync** waiting for an NVIDIA-driver lock;
- call originated in `Verifier::fetch_dma` inside the verify window;
- native IQ packs copied missed experts using host `cudaMemcpyAsync` + `cudaLaunchHostFunc` while the GPU waited/spun on flags those copies raise;
- CPU expert pool was already fully done/parked.

Q2_0 had always used a GPU copy kernel instead and did not show this stall class in the maintainer's soaks.

### 0.1.14 fix

`--pcie-mode auto` now uses the **GPU copy kernel for every pack**, so no host CUDA call is required inside the verify window. `--pcie-mode dma` remains as the old A/B path.

Measured cost on IQ3_S: **45.3 -> 44.8 TG**, about **1%**.

The maintainer closed #31 based on the dumps and fix. However, by this pass's cutoff there is **no independent exact-RTX-5070-Ti post-0.1.14 clean soak yet**.

### P51 status

Upgrade the diagnosis from 'suspected host/GPU handshake bug' to **specific host DMA/driver-lock mechanism with a landed fix**.

Do **not** remove the production gate yet. Require the exact 5070 Ti to complete:
- multi-hour IQ3_XXS/IQ3_S soak
- long degenerate generation / HumanEval-47 style repro
- Q4 KV, spec4
- zero watchdogs / zero dumps.

If that passes, the liveness objection can be substantially downgraded. The ~1% decode cost is trivial relative to production stability.

---

## RECOVERED CURRENT — oMLX Flash-Next GDN prefix-cache boundary snapshots remain unavailable

Issue #4051 was created **2026-09-28 08:53:45 UTC**, ten seconds before the previous boundary, and was missed there. Its current body was not edited after creation, so it is safe to recover now.

Reported setup: M3 Ultra 256 GB, Jundot Qwen3.8-Flash-Next oQ4e-mtp, oMLX 0.7.0rc1, hot + SSD cache, GDN SSD split.

The reporter sees every multi-turn cache store skipped with:
`boundary_snapshot_unavailable ... available_boundaries=0`

Although rc1 gives large decode gains over dev2 in the reporter's harness, repeated 27K prefixes still cold-process all 27K tokens after a cold start. Same-session repeated requests improve, but durable/reusable recurrent boundaries are reportedly absent.

### P51 consequence

This independently reinforces our hybrid-cache rule:
- KV/partial-block reuse is not enough;
- a reusable GDN session prefix needs a **committed recurrent snapshot at the exact cache boundary**;
- if no such snapshot exists, fail closed and re-prefill rather than pretending the prefix is reusable.

For CUDA-prefill -> M1 decode, exported state is not complete until the recurrent checkpoint and its boundary lineage exist alongside KV/QSA/indexer state.

---

## NEW — SGLang moves hybrid radix-cache state capability from hard-coded architecture names toward state specs

PR #41165 merged **2026-09-28 09:07:36 UTC**.

Predicate-registered linear-attention models can now receive Mamba/radix-cache extra-buffer leaves from the registered model spec instead of requiring a hard-coded architecture-name set.

No speed/accuracy measurement was involved.

### P51 consequence

Our state-export/cache layer should be **capability/spec driven**, not model-name driven. A model advertises which recurrent/extra state participates in cache and transfer; the scheduler consumes that spec. This will age better across Qwen4/Flash successors than architecture allowlists.

---

## Edge item deferred by the strict cutoff

Strata issue #53 was opened at **2026-09-28 10:51:11 UTC**, only 20 seconds before this pass's cutoff, but its currently visible body was edited at **10:52:41 UTC**, after the cutoff.

It concerns sampler/penalty parity and may be important for quality certification. **Do not import its current claims into STATE yet.** It is first priority for the next scan.

MLX-Serve #605 (Qwen3.8 agent reporting truncated file reads) was also reviewed. It currently has no server log, minimal reproduction, or evidence separating model/tool-output truncation from the serving engine, so it is **not promoted**.

---

## Strict-window source scan

From **08:53:55 -> 10:51:31 UTC**:
- **TensorFold:** 0.3.6 / 0.3.6.1 released; SSD PLE/expert streaming and M1–M4 chunk-boundary caveat promoted.
- **Strata:** 0.1.14 lands the DMA-driver-lock fix; promoted, exact-5070-Ti validation still pending.
- **oMLX:** no new commit in-window; recovered #4051 recurrent-cache boundary failure.
- **SGLang:** predicate/state-spec hybrid radix-cache support promoted as design evidence.
- **mlx-serve:** no in-window commit; #605 insufficiently isolated, not promoted.
- **Ishizuki:** no in-window commit.
- **MTPLX:** no in-window commit.
- **Splash:** no in-window commit.
- **DFlash upstream:** no in-window commit.
- **vLLM:** no P51-primary in-window runtime commit.
- **llama.cpp:** no P51-primary in-window result.
- **DASLab / GSQ-RCO:** no new strict-window AA-quality receipt.
- **community/HF scan:** no new independent M1 or dual-M1 receipt beyond material already tracked.

---

## Project 51 actions promoted by this pass

1. **Strata 0.1.14 exact-card soak becomes the immediate 5070-Ti gate.** Re-run the same failing long-generation workload before doing more performance tuning.
2. **Freeze chunk-plan identity in AA/PP comparisons.** Add 8K-tail boundary cases and record chunk plan in exported-state fingerprints.
3. **Add parser/tool-protocol correctness to AA.** Empty-turn/tool-call loss is a runtime quality failure even when model logits are fine.
4. **Keep TensorFold SSD experts as a source-identical capacity fallback**, not the canonical performance lane.
5. **Hybrid prefix/export state must include a committed GDN boundary snapshot.** KV/QSA alone is insufficient.
6. **Model state support should be spec-driven**, not architecture-name allowlists.

---

## Canonical planning effect

**No target changes.**

Strata's 0.1.14 diagnosis materially improves confidence that the exact-5070-Ti liveness problem is fixable at very small throughput cost, but we need the reporter's clean soak before calling it solved.

TensorFold 0.3.6 materially improves the memory/capacity fallback story for Flash-Next on 64-GB Macs, but full SSD expert streaming at 0.31–0.39x resident speed is not evidence for the 40-TG dual-M1 lane.

Keep **40 TG @ genuinely filled ~128K / 400 cold PP / ~70% >=40 confidence**, and single-M1 dense **25 TG / ~110 PP**.

## New hard boundary

**2026-09-28 10:51:31 UTC**
