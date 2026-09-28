# Project 51 primary-lane research watch — 2026-09-28 04:53 ET

**Freshness boundary entering this pass:** **2026-09-27 23:23:40 UTC**.  
**User cutoff:** **2026-09-28 08:53:55 UTC**.

Older material that only became fully inspectable after the prior cutoff is labeled UPDATE / RECOVERED CURRENT rather than silently reclassified as new.

## Decision

**No canonical target change.**

Keep:
- dual-M1 Flash-Next: **40 TG sustained at genuinely filled ~128K**
- dual-M1 Flash-Next: **400 realistic cold PP**
- planning confidence for >=40 TG: **~70%**
- single-M1 dense 27B: **25 TG canonical / ~110 native cold PP**
- RTX 5070 Ti + Strata: experimental Flash lane, still **not production-qualified**
- Flash source-like quant search: roughly **3.0–3.6 transformer BPW**, with AA certification still required

This pass materially strengthens the **single-M1 exact-verifier** case and the **~110 PP** ruler, but does not provide a new dual-M1/TB4 Flash-Next receipt at filled 128K.

---

## NEW — direct M1 Max 32-core / 64-GB TensorFold DFlash2 receipt

Source: TensorFold issue #48, comment created **2026-09-28 00:23:31 UTC**.

Hardware and runtime:
- **M1 Max Mac Studio, 32-core GPU, 64 GiB**
- macOS 27.2
- TensorFold 0.3.5 at a3274f1d9df2ba93d1c523c20c6bc18ea5008865
- MLX 0.32.2 / mlx-lm 0.31.3
- target: Qwen3.8-27B affine **4-bit / group 64**
- DFlash2: z-lab Qwen3.8-27B-DFlash2, drafter bits 4
- one stream, greedy, thinking off, context configured 65,536

Stock 0.3.5 would not start on M1 because its simd_qmm launched 512 physical threads while this compiled M1 kernel is capped at **448**.

The reporter applied a narrow workaround: physical simdgroups **16 -> 8**, so the threadgroup becomes 512 -> 256 threads. Crucially, this **does not change the arithmetic split count S or the reduction tree**; remaining arithmetic chunks are walked by the smaller physical group. Startup exactness checks still reported windows up to 16 rows reproducing one-row steps.

Paired results:
- short generation: **16.96 TG serial -> 33.64 TG DFlash2**
- short answer wall: **5.73 -> 3.23 s**
- 6,566-token Rails prompt + <=256 output: **77.05 -> 70.14 s**
- exact cached repeat: **15.75 -> 9.73 s**
- subscription coding/tests: **34.20 -> 15.11 s**
- query repair: **5.65 -> 4.10 s**
- N+1 repair: **61.64 -> 49.56 s**
- three Ruby tasks total: **101.50 -> 68.78 s**
- peak process footprint: **18.57 -> 20.57 GiB**
- no new swap activity in either arm

All **8 corresponding responses had matching token_sha values**, including the repair response. DFlash telemetry showed 64 accepted / 154 proposed tokens on the short fixture and 450 / 719 on the subscription task.

The reporter separately says cold processing of the ~6.6K prompt took about **61 s**, which implies approximately **108 PP**. That is derived from the reported prompt length/time, not a server-reported PP counter.

Limitations:
- one paired run
- short-context decode fixture
- thinking disabled
- not a filled-64K endurance test
- one baseline coding subtask overlapped a CI worker

### P51 consequence

This is the strongest physical Apple7 evidence in the current research set for the exact-row DFlash architecture:
- it directly supports the plausibility of our **~30 TG mixed-use engineering band** on a single M1 Max;
- it independently lands almost exactly on our **~110 cold-PP** single-M1 ruler;
- it validates separating **physical threadgroup occupancy** from the **logical arithmetic split/reduction order**.

It does **not** justify raising the 25-TG canonical ruler yet, and it gives **zero direct numeric credit** to the dual-M1 Flash-Next 40-TG-at-128K target.

---

## NEW — TensorFold 0.3.5.1 upstreams the Apple7/Apple8 physical-threadgroup fix

Commit beddbb7bc818b432163c30500aea256e2b46ff8a at **2026-09-28 02:47:31 UTC**.

TensorFold confirmed that Metal's maximum threads per threadgroup is **per compiled kernel** and falls with register use. For the relevant row matmul:
- M1/M2 can cap below the launch shape; the failing M1 path allowed only **448** threads;
- 0.3.5 launched 512 and failed at load;
- 0.3.5.1 probes/fits a new kernel plan and reduces physical simdgroups when necessary;
- the arithmetic split count and summation order stay unchanged, preserving serial/draft equality;
- other >256-thread kernels now declare/reserve their required pipeline size.

M3/M4/M5 machine code is unchanged.

This is the upstream form of the same workaround used in the M1 receipt above. There is not yet a separate post-0.3.5.1 M1 performance rerun, so do not double-count it as a second speed receipt.

---

## NEW — mlx-serve independently hits and fixes the same M1/M2 Metal threadgroup limit

Commit 2496d200148c2526d0fc6c618814f7271a89543b at **2026-09-28 03:40:21 UTC**.

mlx-serve's TensorFold-derived simd_qmm initially failed CI on M1/M2 for the same reason:
- the MMA kernel used 1024 or 512 physical threads;
- M1/M2 compiled-kernel limits for this path were observed at **704 / 448** depending on specialization;
- M3+ allowed 1024.

The fix caps the logical split at 16, probes a fresh plan, and on a threadgroup-size failure halves the **physical** simdgroups while traversing the same S chunks in the same order. Other failures decline the shape to rowqmv.

M4 Max A/B was flat after the fix.

### P51 rule promoted

Treat these as separate dimensions:
- **logical reduction partition / S** — changes bits and exactness;
- **physical simdgroups resident in one threadgroup** — scheduling/occupancy and chip-limit choice.

On Apple7, do not bake one 512/1024-thread launch assumption into the verifier. Probe/fail-closed by **compiled kernel + shape + dtype**, while holding the arithmetic tree fixed.

---

## NEW MERGE — oMLX lands row-exact Qwen3.8 Flash-Next Lightning MTP

Core merge: d403e4605fc49b5745ca0dc6b71abfa1ff2eb8c3 at **2026-09-28 05:00:02 UTC** (#4023).

oMLX identifies four independent reasons a Qwen3.8 Flash-Next verify row could disagree with serial decode:
1. quantized projections, including lm_head, used different multi-row qmm arithmetic;
2. GDN q/k normalization differed between one-row decode and verify;
3. dense attention changed arithmetic/kernel plan at multi-row widths;
4. gathered QSA selected/rounded differently from the serial path.

The fix routes row-exact verify through one-row-equivalent quantized projection arithmetic, aligns GDN normalization, and executes each attention/QSA row on the serial schedule.

Correctness receipts on the real model:
- R=1..4 windows at ~1.2K, 3K and 2016->2088 crossover contexts
- masked and gathered QSA
- rejected windows + rollback
- **max |Δlogit| = 0**
- four realistic 400-token prompts: MTP on == MTP off byte-for-byte

On M5 Ultra / Qwen3.8-Flash-Next-oQ5e-mtp, exactness itself costs about **0.8 ms per verify cycle / ~3.5% MTP decode** versus the same branch with row-exact disabled. That is M5 evidence only.

### Boundary correctness matters

A follow-up found that even the supposedly exact path failed near MLX attention plan changes:
- around **1,024 keys**, 13 of 47 two-row windows differed because row 0 inherited row 1's two-pass SDPA plan;
- max |Δlogit| reached **1.29**;
- additional boundaries appeared around **16,384** and block-selection ties.

Exactness therefore needs explicit tests at every runtime plan transition, not just random contexts.

---

## NEW — oMLX fuses the exact verifier and recovers most of its performance cost

PR #4041 merged as e15e5b537f511b8e0000ff58113a946139b4448d at **2026-09-28 05:10:53 UTC**.

Before the fusion, roughly 90% of an MTP cycle could sit in the target verify window. oMLX reduces:
- MoE verify to **4 launches/layer**
- GDN verify to **3 launches/layer**, preserving per-step FP32 recurrent state and rollback records
- masked-QSA verify to the same selected-key path used by serial decode
- R=1 speculative cycles directly to the serial step

M5 Ultra / oQ5e measured:
- coding MTP: **159.3–159.9 -> 175.4 TG (+10%)**
- another MTP workload: **179.5–181.0 -> 195.7 (+8.5%)**
- MTP-off: flat at ~111 TG
- 24K PP: flat at ~3,947
- short R=4 verify: **17.1 -> 15.0–15.2 ms**
- 24K R=4: **22.3–22.5 -> 18.6–20.1 ms**
- host CPU per short R=4 window: **12 -> 7 ms**

The fused path remained bit-identical to serial across 1K/16K plan transitions and partial-accept recurrent rollback.

### Important negative result: exact routing cannot be global

A separate M5 Ultra oQ6e report shows that arming the exact per-row path for every batched verify can destroy throughput:
- baseline aggregate c=1/c=4/c=8: **150 / 173 / 199 TG**
- row-exact global: **153 / 135 / 108 TG**
- full exact chain: roughly **157–174 / 136–142 / 105–107 TG**

Gating row-exact to **single-stream verify** recovered approximately **176 / 176 / 200 TG**. A prompt-lookup path with 8–15 verify rows also fell **273 -> 199 TG** under per-row exact mode; limiting that exact route to <=4 rows restored throughput.

### P51 rule promoted

Exactness routing must be keyed by at least:
- Apple generation / compiled kernel
- quant width and shape
- verify width S
- number of concurrent streams B
- attention/QSA plan boundary
- greedy vs sampled semantics

Do **not** globally replace all multi-row paths with a one-row-equivalent kernel.

---

## UPDATE — row-exactness is GPU-generation-specific and includes sampler semantics

On M3 Ultra, oMLX found a one-ulp GDN beta mismatch: a fast bf16 exp differed from mx.sigmoid. Commit 8cc7812f at **06:16:57 UTC** fixes it.

Open PR #4050, created **06:49:09 UTC**, adds a per-device row-exact diagnostic covering:
- qmv copies versus stock MLX
- SDPA transitions at 1,024 / 4,096 / 8,192 / 16,384 / 65,536 keys
- GDN 6/8-bit paths
- HC R=1..8
- MoE
- dense/masked attention
- PLE conv

It also finds a device-independent sampler discrepancy: serial greedy picks from bf16 log-probabilities, while verify had picked raw-logit argmax. Near ties can therefore select different token IDs even when the logits look equivalent.

### P51 consequence

Our verifier certification must test **the actual emitted token rule**, not merely logits, and it must run on the M1 itself. Add explicit plan-boundary vectors and near-tie sampler cases to P69B13 certification.

---

## UPDATE — the deferred oMLX idle/wake issue is now promotable and is directly relevant to M1 agent latency

oMLX issue #4040 was deliberately deferred last pass because its visible body was edited after the previous cutoff. It is now in-window.

Measured setup:
- **M1 Ultra 64 GB**
- macOS 27.0
- MLX 0.32.2
- 41.8-GB Qwen3-Coder-Next MLX 4-bit model

After roughly >=2 s without a model forward:
- first forward: approximately **862–1,012 ms**
- immediate repeat: **20–27 ms**
- estimated wake cost scales around **12–22 ms per resident GB** in this experiment

With default unwired memory, trivial GPU keepalive calls do **not** prevent the expensive first model-weight read. With a bounded wired limit, a trivial GPU command every 0.5 s keeps the next model forward around **40–49 ms**.

oMLX #3974, merged in-window, adds a 0.5-s GPU keep-warm ticker while a model is loaded. On an M5 Ultra / 156-GB MiMo model it removed a 1–1.7-s idle wake penalty. But the M1 #4040 measurements indicate that keep-warm alone is insufficient while weights remain unwired.

### P51 consequence

Add an **idle-gap TTFT ruler**:
- 0.5 s
- 1 s
- 2 s
- 5 s+

Measure separately:
- unwired weight-page wake
- generic GPU idle-state wake
- hot-prefix restore
- first decode after restored state.

For a multi-minute cold 128K prefill this cost is noise; for a ~0.24-s hot-cache turn it can dominate user-perceived latency.

Do not blindly wire all memory: use a bounded wired budget with OS headroom and recheck long-running memory behavior.

---

## NEW — oMLX Qwen prefill stack gives more mechanism evidence, but mostly M5-only numeric credit

Several Qwen prefill PRs merged in-window:
- #3980: widen later Qwen4 prefill chunks
- #3981: use a wide first chunk when PLE is resident
- #3982: exact HC prefill fusions + depthwise PLE conv
- #4006: software-pipelined GDN recurrence
- #4020: NAX QSA attention

The most transferable item is #4006: for Hk=16/Hv=48 at T=8191, the GDN recurrence itself fell **4,933 -> 2,880 us (1.71x)** on M5 Ultra via software pipelining while retaining the per-step recurrence structure. End-to-end PP improved only ~3–4% because other components dominate.

#4020's QSA tensor-unit path gives larger M5-only long-context PP gains, but it is NAX-specific and receives zero Apple7 numeric credit.

### P51 consequence

Keep **whole-chunk / software-pipelined GDN on Apple7** near the top of the PP experiment queue, but require an M1 measurement before moving the 400-PP dual-M1 forecast.

---

## NEW — Strata 0.1.13 approximately doubles long-prompt throughput on the weaker RTX 5070 12-GB card

Commit 928b0e0721b75677235e8c233559a9fc5a172f60; release v0.1.13 created **02:56 UTC**, published **05:09 UTC**.

Measured hardware: **RTX 5070 12 GB + Ryzen 5 7600 + 64 GB DDR5** — not the user's 5070 Ti.

32K prompt throughput:
- Q2_0: **572 -> 1,290 PP**
- IQ3_S: **383 -> 1,208 PP**

Server, Q2_0 with 128K context:
- 999-token prompt: **353 -> 438 PP**
- 6,927: **529 -> 1,077 PP**
- 28,584: **584 -> 1,249 PP**

Main mechanisms:
- adaptive prompt chunks up to 8,192
- shared attention/MoE scratch
- whole-chunk PLE
- llama.cpp MMQ expert kernels with quantized weights / int8 activations
- fixed-order ring streaming of nonresident experts overlapped with attention
- helper threads for unpinned host copies

Needle tests were reported 5/5 from 1K through 262K.

### Quality caveat

Not every new prompt path is bit-identical. On a 32K teacher-forced comparison:
- alternate chunking yardstick: **89.8% same top-1, mean KL 0.33**
- MMQ experts: **85.9% same top-1, mean KL 0.38**

That is useful engineering evidence, not source-like AA certification. Do not let the PP headline silently enter the AA~40 baseline.

Two correctness bugs in the new path were fixed later in the same window and before the release creation point:
- stale bytes beyond the last gathered expert could produce NaNs / repeated '!!!!' answers;
- prompt-layout initialization could overwrite a resident expert cache slot and corrupt later decode.

---

## UPDATE — Strata 0.1.13 proves the remaining 5070 Ti stall is no longer the CPU expert pool

The exact **RTX 5070 Ti 16 GB** reporter caught two new 0.1.13 stalls with the new diagnostics:

First, around **46 min**:
- verify layer 27
- 24/24 expert jobs claimed and done
- 7/7 workers parked/sleeping
- host idle ~60 s
- GPU ring had advanced to the expected step
- ~1.9 GiB RAM available

Second, around **21 min** into a clean rerun:
- verify layer 1
- 24/24 jobs complete
- all workers parked
- host idle >60 s
- GPU ring again reported the next step
- ~8.5 GiB RAM available

The very different free-RAM levels weaken memory pressure as the common cause. The common signature is now **host waiting in the GPU-side layer handshake even though the GPU sequence/ring has advanced**.

The watchdog limits the hang, but recovery is not cheap: after the first 0.1.13 self-stop, the reporter says the cold engine reload took about **15 minutes**, causing the remaining 74 benchmark requests to error during reload.

### P51 status

Keep Strata behind the production gate. The prior CPU-pool race was real and fixed, but a second liveness mechanism remains, likely in the CUDA/host synchronization/protocol path. A watchdog is mitigation, not production readiness.

---

## NEW — real-model hybrid PD parity strengthens our CUDA-prefill -> M1-import test design

SGLang #41378 merged at **2026-09-28 03:23 UTC**.

Using real Kimi-Linear-48B-A3B-Instruct in deterministic mode, SGLang now checks prefill/decode disaggregation across:
- 16-token page boundaries
- 32-token DCP virtual-page boundaries
- 64-token chunk boundaries
- cached-prefix radix hits at 64 / 128 / 256 tokens

The oracle is exact emitted tokens plus logprob delta <=1e-3 where the execution topology has a valid monolithic reference. Heterogeneous-TP cases were deliberately removed because bit-exact comparison is not a valid oracle across those different topologies.

### P51 consequence

Our 5070-Ti prefill -> MLX decode bridge should explicitly test:
- just before / on / just after transfer page/chunk boundaries
- cold versus cached-prefix state export
- recurrent state + KV + QSA/indexer + positions together
- exact tokens where the numerical topology permits it
- tight logit/logprob tolerances rather than fake bit-exactness when CUDA and MLX necessarily use different arithmetic.

---

## NEW — vLLM reuses GDN metadata instead of rebuilding it per cache group

PR #58762 merged at **2026-09-28 04:36 UTC**.

On Qwen3.6-35B-A3B + DFlash with 46 cache groups, B200 measurements report:
- c=1 step time **-40%** versus main
- c=1 output **+57%**
- c=32 output **+23%**
- CUDA API calls/step **1,032 -> 424**
- acceptance length and GSM8K unchanged

The mechanism is more important than the B200 percentage: groups sharing the same Mamba/GDN spec can share batch-level metadata and only update the state indices/block table.

### P51 consequence

For our hybrid cache/state scheduler, **do not rebuild equivalent recurrent metadata for every logical group or transferred shard**. Reuse the batch-level plan and vary only the state mapping needed by that group.

---

## Strict-window source scan

From **2026-09-27 23:23:40 -> 2026-09-28 08:53:55 UTC**:
- **TensorFold:** M1/M2 loader/threadgroup fix plus the direct M1 Max DFlash2 receipt; promoted.
- **mlx-serve:** M1/M2 simd_qmm fit fix, all-chip verify-row enablement, disk-cache billing fix, sampled greedy-tail experiment; relevant items promoted selectively.
- **oMLX:** major Qwen exact-decode/verify/prefill merge wave; promoted. Typical+greedy-tail remains behavior-changing and stays outside exact baseline.
- **Strata:** 0.1.13 major PP work, prompt-path correctness fixes, and new 5070-Ti stall diagnostics; promoted.
- **SGLang:** real-model hybrid PD parity; promoted.
- **vLLM:** recurrent metadata reuse; promoted.
- **Ishizuki:** no in-window commit.
- **MTPLX:** no in-window commit.
- **upstream Splash:** no in-window commit.
- **DFlash upstream:** no in-window commit.
- **llama.cpp:** no qualifying P51-primary inference commit.
- **DASLab / GSQ-RCO:** no new strict-window quant-quality certification receipt.
- **TensorFold / SGLang / others:** no new physical dual-M1/TB4 Flash-Next @ filled ~128K receipt.

---

## Project 51 actions promoted by this pass

1. **P69B13 becomes a physical-SG / logical-S separation experiment.** Keep the exact arithmetic partition fixed; probe the number of physical simdgroups the compiled M1 kernel can sustain.
2. **Port/cross-diff oMLX #4023/#4041 exactness cases into the verifier suite:** 1,024 / 4,096 / 8,192 / 16,384 / 65,536 attention transitions, QSA selection ties, GDN partial rollback, near-tie greedy sampling.
3. **Dispatch exact verify by chip x quant x shape x S x B.** Single-stream S=2–4 can deserve an exact fused route; wide PLD and B>1 must have independently measured routes.
4. **Add the M1 idle-gap TTFT ruler** and test bounded wiring + keep-warm as a pair, not keep-warm alone.
5. **Single-M1 production ruler:** reproduce the new TensorFold M1 receipt ourselves with xhigh/thinking and 30K/64K contexts; the public result now gives a credible target to match.
6. **Apple7 PP:** prioritize software-pipelined/whole-chunk GDN and component timing before porting NAX-only QSA ideas.
7. **Strata:** keep 0.1.13 for PP experimentation only; do not use its current MMQ path as an AA~40 baseline until quality is certified, and do not call the server production-stable until the GPU/host handshake stall is fixed.
8. **PD import matrix:** add page/chunk/cache-hit boundary parity and topology-aware token/logit oracles.
9. **Cache scheduler:** reuse recurrent/GDN metadata across equivalent groups; count API/host planning calls separately from actual target math.

---

## Canonical planning effect

**Dual-M1 targets remain unchanged.**

The M1 Max 33.64-TG DFlash2 receipt and ~108-PP derived cold prompt rate materially increase confidence in the **single-M1 dense27B engineering plan**, especially the ~30-TG mixed-use / ~110-PP neighborhood. They do not establish long-context xhigh performance and therefore do not replace the conservative 25-TG canonical ruler.

For the dual-M1 Flash-Next target, the new evidence improves confidence in the **mechanisms** — exact few-row verification, Apple7 physical-threadgroup fitting, recurrent prefill pipelining, cache/state control — but there is still no physical dual-M1/TB4 Flash-Next 128K run. Keep **40 TG @ ~128K / 400 cold PP / ~70% >=40 confidence**.

## New hard boundary

**2026-09-28 08:53:55 UTC**
