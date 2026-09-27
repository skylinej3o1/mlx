# Project 51 primary-lane research watch — 2026-09-27 14:28 ET

**Freshness boundary entering this pass:** **2026-09-27 17:22:18 UTC**.  
**User cutoff:** **2026-09-27 18:28:19 UTC**.

This pass preserves the strict boundary. Same-day material that predates the boundary but was missed in prior watches is labeled **RECOVERED CURRENT** or **SAME-DAY CURRENT**, not NEW.

## Decision

**No canonical target change.**

Keep:
- dual-M1 Flash-Next: **40 TG sustained at genuinely filled ~128K**
- dual-M1 Flash-Next: **400 realistic cold PP**
- planning confidence for >=40 TG: **~70%**
- single-M1 dense 27B: **25 TG canonical**, **~110 native cold PP target**
- 5070 Ti + Strata Flash lane: **first-class experimental runtime candidate**, but not production-qualified

This pass materially changes two experiment priorities:

1. **Apple7 long-context execution must bound individual Metal command duration**, not merely total TTFT/PP.
2. **Strata on the exact RTX 5070 Ti now has a demonstrated nondeterministic hard-wedge/liveness problem**, so stability testing is a promotion gate, not a nice-to-have.

---

## NEW — Splash 1.1 M1 branch: weight residency fixes cache-state admission and clears ~120–130 PP at 30K

Source: https://github.com/paperniuk/splash/commit/c5f93c964e58d3ba45c4e7e617b2e60ccae99b7c  
Committer time: **2026-09-27 17:29:34 UTC**.

The M1/M2 Splash 1.1 branch reverts an attempted policy that removed file-backed model weights from the Metal residency set.

Observed on **M1 Max 64 GB / Qwen3.8-27B**:

- without weight residency, host-available memory swings from about **54.0 GB idle -> 37.7 GB while serving**;
- with the weights resident, it stays around **38.0 -> 36.9 GB**;
- on 32-GB systems the apparent swing can push the memory governor below its **1-GB headroom margin**, deny a GDN-state snapshot, and make every request report **cached 0**;
- after reboot + resident weights, the 27B:
  - prefills **~8K in 61 s**;
  - prefills **~30K in 243 s**;
  - keeps cache across a growing chat;
  - passes the fork's **54/54** task eval.

The approximate prompt-rate implications are in the **~120–130 PP class**, directly on M1 Max. This is important physical evidence for the P51 single-M1 **~110 PP** planning target, but it does **not** promote a higher target yet because:
- this is an unreleased 1.1 branch;
- the Splash package/quant identity is not the frozen P69 identity;
- 54/54 is a regression/quality smoke test, not AA-class certification.

**P51 rule:** memory-residency policy changes the measurement itself. A live-memory governor must not interpret command-time wiring of file-backed weights as actual new working-set growth and then deny recurrent/cache checkpoints. Record **resident/wired/file-backed/shared** memory separately.

---

## RECOVERED CURRENT — Splash M1 bounded-prefill commands prevent macOS watchdog aborts at deep context

Source: https://github.com/paperniuk/splash/commit/4083ec6ad33167fe7f0d454b6449ea91f8f2000a  
Committed earlier the same day (**12:14 UTC**) and missed in the previous consolidation.

On M1, one full 2,048-row long-context prefill dispatch can become an extremely long single GPU command:

- about **12 s per full command around 8K**
- about **~1 minute per full command around 170K**

macOS aborted such a command with **ImpactingInteractivity** during a long agent session.

The fix dynamically halves isolated prefill work to keep an individual command around **<=5 s**, while retaining the existing tighter bound when another request is waiting.

ABBA on **M1 Max / Qwen3.8-27B**:

- 8K cold TTFT: **60.8 s vs 60.9 s**
- 30K cold TTFT: **269.0 s vs 269.1 s**

So command splitting is approximately **throughput-neutral** on these measurements. An 8K prefill becomes **17 commands instead of 5**.

Most important: a **7-hour agent session reached 229K context without an abort**; the prior build failed at **176K**.

**P51 consequence:** for Apple7 PP, total PP is not a sufficient health metric. Add:
- max Metal command duration;
- command-buffer count per chunk;
- watchdog/ImpactingInteractivity events;
- GPU reset/wedge detection.

For the dual-M1 Flash PP2 lane, target a command-duration envelope that preserves long-agent liveness without sacrificing aggregate PP. This is independent of the whole-chunk-GDN idea: a whole-chunk recurrent kernel may still need a bounded outer command.

---

## RECOVERED CURRENT — Apple7 generic GGUF kernels close much of the runtime-format gap

Source: https://github.com/paperniuk/splash/commit/15abab5b1d2660ef8dc872d5ce57deac14022eaf  
Committed **2026-09-27 13:36 UTC**, before this strict window.

The Splash M1 branch adds simdgroup-MMA GGUF kernels for Apple7/8 because upstream MPP paths were effectively unusable on M1 for these shapes.

On **M1 Max 64 GB / unsloth Qwen3.8-27B UD-Q4_K_M**:

- **31.6 TG** on the five npanj prompts;
- Splash's own Q4 package on the same benchmark is about **38 TG**;
- 8K cold TTFT: **65.9 s** vs **62.8 s** for the Splash package;
- word-problem smoke suite: **54/54**.

**Interpretation:** a substantial fraction of the apparent format/runtime gap on Apple7 was kernel quality, not an immutable GGUF limitation. This is supporting evidence for mining low-bit GGUF/GSQ arithmetic without assuming stock MLX or stock llama.cpp execution cost.

No canonical P51 target credit: short-prompt TG and a 54-item smoke test are not our deep-context/AA ruler.

---

## NEW — Splash 1.1 Apple7 vision kernels

Source: https://github.com/paperniuk/splash/commit/3050f5c7317fdc797956af3da222eefdc106124f  
Committed **2026-09-27 18:10:15 UTC**.

Apple7/8 gets custom simdgroup-MMA vision GEMM/attention kernels rather than MPP emulation.

M1 Max parity fixtures:
- Qwen3.8-27B relative error **0.0142**, worst cosine **0.9999**
- Qwen3.6-35B-A3B relative error **0.0293**, worst cosine **0.9972**
- 64x64 grid / 1,024 vision tokens: **872 ms**
- 128x128 maximum grid completes deterministically

This is useful for eventual multimodal completeness, but it has **no current text TG/PP target effect**.

---

## NEW — Strata #31: exact RTX 5070 Ti has a reproducible hard-wedge/liveness failure

Source: https://github.com/Niko1221/Strata/issues/31  
Created **2026-09-27 18:27:53 UTC**, only seconds before this pass's cutoff.

This is the first high-value failure report in the exact GPU class of the user's secondary rig:

- **RTX 5070 Ti 16 GB (SM120)**
- Windows
- Ryzen 9800X3D / 63 GB RAM
- Strata engine v0.1.9
- **Swift-Qwen3.8-Flash-Next-GSQ-RCO-IQ3_XXS**
- max context 262144
- **Q4_0 KV**
- 32K resident KV
- native speculation depth 4
- expert cache: **5,059 slots / 8.21 GiB**
- boot free VRAM: **707 MiB**
- streamed K/V: **1.69 GiB pinned RAM**

Across ~2.5 h of sustained single-request benchmarking, the reporter captured **four hard wedges**.

Common signature:
- generated-token counter becomes completely static;
- elapsed time continues;
- GPU reports **100% utilization at ~69 W**, i.e. low-power/spinning rather than useful compute;
- CPU stops doing useful work;
- VRAM remains allocated;
- process stays alive;
- client timeout/cancel does not unwind the request;
- the single server slot remains permanently blocked.

The freeze happened at very different points:
- **13 generated tokens**
- **130**
- **218**
- **91,058**

One exact replay of the frozen code task succeeded immediately after restart, so the failure is **not deterministic by prompt alone**.

Healthy requests between failures ran around **50–90 TG**, and one long degenerate output was around **105 TG** before wedging, but these are workload observations rather than a controlled 128K performance ruler.

**P51/5070-Ti consequence:** this is now a mandatory blocking promotion gate. Before calling Strata a daily-driver Flash server on the user's card, run a multi-hour soak with:
- spec on/off;
- Q8 vs Q4 KV;
- streamed vs more-resident KV;
- fixed expert-cache/reserve;
- progress watchdog;
- GPU power + utilization;
- CPU worker state;
- last completed CUDA event / stream position if exposed;
- cancellation recovery.

The raw performance thesis remains alive; the **runtime-readiness confidence decreases**.

---

## UPDATE — Strata #29 suggests the wedge is not simply INT8 KV

Source: https://github.com/Niko1221/Strata/issues/29

Before the 18:28:19 cutoff, the 4090 reporter reproduced the same no-progress signature after switching from INT8 KV to **Q4_0 KV**, freezing around token **9,132**.

The maintainer said they believed they knew the reason and intended to patch it, but **no root-cause explanation or landed fix existed by this pass's cutoff**. Therefore:
- do not count the maintainer statement as a fix;
- do not blame INT8 alone;
- #31's Q4_0 reproduction on 5070 Ti independently reinforces that caution.

---

## NEW — SGLang #39726: page-unified KV load-back reaches near-PCIe-copy bandwidth, but overlap quota matters

Source: https://github.com/sgl-project/sglang/pull/39726  
Merged **2026-09-27 17:45:03 UTC**, commit e581520c67a921feda4433bc4e4d41f3514a9d06.

HiCache can now load page-unified host KV pages back **one layer at a time** directly from pinned host mapping into the device pool.

Key design:
- no full-page per-layer staging;
- each thread moves 16 B;
- reads are coalesced across pinned host memory;
- per-layer transfer can overlap the model forward;
- a block-quota cap controls the tradeoff between transfer bandwidth and stealing SMs from forward compute.

B200 / PCIe Gen5 / bf16:
- quota 2: **~15.4–18.2 GB/s**
- quota 16: **~39.7–47.8 GB/s**
- contiguous cudaMemcpyAsync ceiling: **53.8 GB/s**

Correctness:
- **123 cases** against a PyTorch indexing reference;
- page write-back -> load-back round trips are bit-identical across 9 configurations.

**P51 transfer lesson:** remote-prefill/import pipelines should expose transfer concurrency as a measured scheduler knob. Maximum copy bandwidth is not necessarily maximum end-to-end throughput if transfer work competes with forward compute. Imported state should become visible **layer-by-layer only after that layer's transfer is complete**.

This is CUDA/B200 transfer evidence, not M1/TB4 numeric credit.

---

## SAME-DAY CURRENT — MoEspresso 3 proves a very-low-memory M1 Flash-Next configuration, but it is behavior-changing

Public sources:
- Reddit: https://www.reddit.com/r/LocalLLaMA/comments/1wrqql8/
- model card: https://huggingface.co/steadfastgaze/Qwen3.8-Flash-Next-MoEspressoV3
- engine docs: https://github.com/steadfastgaze/MoEspresso

Exact Reddit publication time was not exposed, so this is **SAME-DAY CURRENT**, not strict-window NEW.

Reported hardware:
- **2021 M1 Max, 24-core GPU, 32 GB unified memory**
- Qwen3.8-Flash-Next
- about **12–15 TG**
- ordinary serving context **128K**

Memory/package strategy:
- all 512 routed experts remain available;
- most routed projections are **IQ2_K**; first two layers use IQ3_K;
- dense/non-routed tensors use Q6_K/Q8/BF16 by role;
- original **~95.37 GiB BF16 PLE/ngram payload stays SSD-backed**;
- older attention cache body uses **K4/V4**, with sink/recent suffix BF16;
- this package excludes the MTP sidecar.

Crucially, decode routing is **not source-identical**:
- the top two original router choices are protected;
- resident experts receive a factor-two ranking preference for the remaining routes;
- selected contributions use original router probabilities renormalized over the chosen set;
- prefill remains unbiased.

The model card's frozen 48-question comparison reports **84.3%** for this bounded local path versus **90.7%** for hosted source Qwen3.8 Flash xhigh under its comparison protocol. This is far too small/narrow to establish AA~40 parity and the routing itself intentionally changes model behavior.

**P51 interpretation:**
- strong capacity proof for SSD PLE + SSD expert streaming on old Apple silicon;
- interesting optional low-memory/throughput lane;
- **zero production AA~40 or 40-TG target credit** because the route set and KV representation are deliberately lossy.

It independently supports our rule: preserve unbiased/source-identical routing in the main lane; use locality-biased routing only as an explicitly separate behavior-changing experiment.

---

## Community watch — Splash quality/stability remains mixed by configuration

A same-day r/oMLX discussion reports:
- M1 Max users liking the fork;
- one M2 Ultra user reporting crashes beyond 64K on the older fork path;
- an M3 Max user reporting three simultaneous agents with >300K cumulative context;
- several users saying Q4 quality is materially worse than higher-precision oMLX/MLX-Serve variants.

These are anecdotes, not receipts. The new M1 1.1 branch's bounded-prefill and residency fixes are stronger evidence and should supersede generic community impressions when the paths overlap.

---

## Strict-window source scan

From **17:22:18 -> 18:28:19 UTC**:

- **paperniuk/Splash M1 fork:** meaningful new 1.1 branch activity; promoted above.
- **Strata:** no new commit, but exact-5070-Ti issue #31 is highly material.
- **SGLang:** page-unified HiCache load-back merged; promoted above.
- **mlx-serve:** only benchmark/documentation tooling after the boundary; no new runtime TG/PP receipt.
- **oMLX:** no new commit or issue update in-window on the P51 Qwen lane.
- **Ishizuki:** no new commit.
- **MTPLX:** no new commit.
- **upstream incoai/Splash:** no post-boundary commit.
- **DFlash:** no new commit.
- **DS4:** no new commit.
- **llama.cpp:** no qualifying post-boundary P51 commit.
- **vLLM:** only unrelated fast-start activity in the commit window.
- **DASLab/GSQ-RCO:** no new strict-window quality receipt.
- **TensorFold:** no new planning-grade M1 physical measurement surfaced.

---

## Project 51 actions promoted by this pass

1. **Apple7 command-duration gate**
   - record longest single Metal command;
   - bound long-context prefill commands to a safe wall-time envelope;
   - validate that chunking is PP-neutral and state/logit-equivalent.

2. **Apple7 memory-accounting gate**
   - distinguish file-backed weight residency/wiring from request-owned growth;
   - ensure memory pressure cannot silently deny recurrent snapshots and collapse cache reuse.

3. **Single-M1 PP reproduction**
   - reproduce 8K / 30K / 64K PP using the new Splash 1.1 Apple7 branch;
   - record resolved row/chunk width, max command duration and actual active context;
   - compare against our 110-PP production ruler.

4. **5070-Ti Strata liveness matrix**
   - Q8 vs Q4 KV;
   - spec 0 vs native MTP/spec 4;
   - 32K streamed KV vs higher-resident arm;
   - multi-hour random + coding + long-generation soak;
   - cancellation and server-recovery behavior.

5. **Transfer scheduler**
   - treat layer-granular transfer visibility and transfer/forward contention as first-class knobs for CUDA-prefill -> MLX import.

6. **Keep MoEspresso Cache-Prior separate**
   - potentially useful locality experiment;
   - never mix its behavior-changing routing numbers into AA~40 certification.

---

## Canonical planning effect

**Targets remain unchanged.**

The strongest positive update is that a current M1 Max 64-GB 27B path is now physically in the **~120–130 PP class at 8K–30K**, strengthening the plausibility of the existing **110 PP** single-M1 production target.

The strongest negative update is that **Strata on an exact RTX 5070 Ti 16-GB system can hard-wedge nondeterministically under sustained use**. This does not invalidate its excellent short benchmark performance; it does prevent promotion to a production/default Flash server until the liveness bug is isolated and fixed.

No new exact dual-M1/TB4 Flash-Next throughput receipt appeared, so **40 TG @ ~128K / 400 PP / ~70% >=40 confidence stays put**.

## New hard boundary

**2026-09-27 18:28:19 UTC**
