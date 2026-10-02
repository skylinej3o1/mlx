# Project 51 research watch — 2026-10-02 08:27 ET

Freshness boundary entering: **2026-10-02 09:52:00 UTC**
Cutoff: **2026-10-02 12:27:00 UTC**

## Decision

**No mature TG/PP center changes and no hardware-purchase change.** Strata **v0.1.35 remains the latest release** and the exact-box plan remains stock Strata first, IQ3_S, native 262,144, one RTX 5070 Ti 16 GB + 64 GB DDR5, vision off initially.

The new evidence mostly tightens qualification:
- do not trust one automatic PCIe calibration sample;
- a configuration must survive the **late** VRAM/weight-arena allocations, not merely boot and sit resident;
- prefix restore + MTP + high cache pressure belongs in the soak matrix;
- MLX-side quality A/Bs need a **batch-shape determinism** gate because current split-K quantized matmul can change arithmetic with M.

The existing **~90% physical-fit prior is unchanged**. The new 262K OOM report is a different topology (dual 22-GB 2080 Ti, vision on, IQ3_XXS, layer split), so it is not evidence strong enough to reverse the prior raised by #469. Likewise, the 8 h / 24 h Strata zero-stall planning priors remain ~75% / ~55%; #481 has a second anecdotal "me too" report but still no diagnosed fix.

## NEW — Strata #486: native262K can fail late even when the topology looks roomy

Issue:
https://github.com/Niko1221/Strata/issues/486

Reported setup:
- Linux / Ubuntu 24.04;
- 2x RTX 2080 Ti **22 GB**;
- 126 GB RAM;
- IQ3_XXS;
- vision enabled;
- layer split;
- INT8 KV, 32,768 resident cells;
- MTP spec4.

At 262,144 context the run reached a **late** allocation failure:
`cudaMalloc(1538035200) weight arena failed` (~1.43 GiB).

The reporter says the host could become effectively unresponsive. The same machine/config family is stable at **204,800** with a 4,096 prefill chunk and explicit reserve.

Interpretation for Project 51:
- this is **not** an exact-user analog and does not lower the 90% host-fit prior by itself;
- it strongly validates the existing transient-peak gate;
- the first exact-box 262K run should remain **vision OFF, MTP OFF**, then add MTP;
- log free VRAM immediately before/after long cold prefill and capture the maximum transient, not only steady resident VRAM.

A configuration that boots but fails a real ~250K cold prompt still fails Project 51.

## NEW — Strata #485 / PR #487: one PCIe probe can materially mistune decode

Issue:
https://github.com/Niko1221/Strata/issues/485

PR:
https://github.com/Niko1221/Strata/pull/487

On the same RTX A3000 12-GB laptop / PCIe 4.0 x16 host, the startup probe read:
- 18.5 GB/s;
- 6.9 GB/s;
- 5.8 GB/s.

Those readings implied `pcie_frac` around 0.39, 0.15 and 0.12 respectively. The host's actual calibration table peaked around:
- 0.00 -> 27.0 TG;
- 0.20 -> 30.1 TG;
- **0.35 -> 32.7 TG**;
- 0.55 -> 32.5 TG;
- 0.75 -> 30.8 TG.

PR #487 changes the probe to prime the link and use the median of five timed bursts. It is still open at this cutoff.

Project-51 exact-box rule until this lands in a release:
1. record the startup PCIe reading on multiple fresh starts;
2. if it moves materially, run `tools/calibrate.py`;
3. do not treat one auto-selected `pcie_frac` as a hardware truth.

This can explain double-digit-percent decode differences without any model or quant change.

## NEW — Strata #489 / #494: CPU expert pool can dominate a low-VRAM decode round

PR:
https://github.com/Niko1221/Strata/pull/489

Profile issue:
https://github.com/Niko1221/Strata/issues/494

Hardware:
- RTX A3000 12 GB;
- i7-12850HX;
- 128 GB RAM;
- IQ3_XXS native pack;
- Strata 0.1.35 profile.

Fresh-decode profile at hit_rate 0.354:
- round: 78.1 ms / 26.9 TG;
- CPU expert pool: **41.6 ms / 53%**;
- GPU "wait for rings": 26.7 ms / 34%;
- MTP drafter: 3.1 ms / 4%.

Warm/degenerate profile at hit_rate 0.756:
- round: 37.3 ms / 30.9 TG;
- CPU expert pool: 9.6 ms / 26%;
- GPU: 23.1 ms / 62%.

The same report says real serve traffic on the host ran about 34-40 TG.

Interpretation:
- the CPU/memory path can be first-order when expert residency is constrained;
- the user's Ultra 7 + DDR5 host should not be modeled as a cosmetic improvement over weak DDR4 hosts;
- but this does **not** justify mechanically raising the IQ3_S TG centers before exact-box measurement.

## NEW — Strata PR #484 exposes useful prefix/cache instrumentation

PR:
https://github.com/Niko1221/Strata/pull/484

Open PR adds monitor/metrics for:
- prompt tokens reused;
- hits when switching conversations;
- parked conversation slots;
- cache RAM;
- evictions.

This maps almost directly to the Project-51 retained-prefix / tool-append / switch-and-return tests. If merged into a stable baseline, capture these counters in the exact-box harness. Do not depend on them while the PR is open.

## NEW — Strata #497: RX 6800 Windows auto expert-cache can overfill the WDDM budget

Issue:
https://github.com/Niko1221/Strata/issues/497

Secondary-hardware relevance only: RX 6800 16 GB / Ryzen 5800X3D / 64 GB / Windows.

Reported IQ3_XXS 131K:
- 0.1.35 zip, `--expert-cache auto`: **31.4 TG**;
- fixed `--expert-cache 3072`: **42.0 TG**;
- local build with proposed Windows budget fix #380, auto: **42.8 TG**.

The report attributes the loss to auto sizing from HIP free-memory numbers that did not respect the Windows process VRAM budget, pushing roughly 1.1 GiB of engine allocations into system memory. It also reports a broken HIP PCIe timing probe with absurd TB/s readings.

This is not the user's Linux RX-6800 topology and does not change the primary 5070-Ti plan. It is a useful warning that **more expert-cache slots can make Windows slower** if they force WDDM migration.

## UPDATE — Strata #481 long-agent deadlock still has no identified fix

Issue:
https://github.com/Niko1221/Strata/issues/481

There is now a second "me too" report, but no useful new stack, reproducer or merged fix at this cutoff.

Keep:
- >=8 h soak mandatory;
- external supervisor in early production use;
- cancellation + immediate retry;
- heavy prefix reuse;
- long xhigh/high reasoning;
- server recovery after engine death.

Do not move the existing ~75% / ~55% 8 h / 24 h zero-stall priors from one terse corroboration.

## NEW — vLLM #59768: async long-prefix restore + MTP + high KV pressure can crash Qwen3.8 Flash-Next

Issue:
https://github.com/vllm-project/vllm/issues/59768

Different runtime, but an excellent stress-shape warning.

Reported setup:
- Qwen3.8-Flash-Next NVFP4;
- SM120 RTX PRO 6000;
- native 262,144;
- MTP3;
- 4-8 concurrent agentic requests;
- requests around 80K-185K;
- CPU prefix offload/restore;
- GPU KV pool at 92-98%.

Five crashes share a pattern:
- a 74K-141K CPU->GPU prefix load is in flight;
- a request is entering first decode after prefill;
- MTP is active;
- high KV pressure;
- CUDA illegal memory access / Xid 13.

The reporter says it recurs roughly every 45-80 minutes under sustained load.

This is **not Strata evidence** and does not lower a Strata runtime prior directly. It does strengthen the generic Project-51 soak case:
**restore/reuse + MTP + near-full memory + immediate decode** must be exercised together, not as separate microtests.

## NEW — MLX #4613: split-K quantized_matmul can be batch-shape dependent

Issue:
https://github.com/ml-explore/mlx/issues/4613

In MLX 0.32.3, the report traces a precision change to split-K `quantized_matmul`: partial sums are stored in the input dtype, so BF16/FP16 rounds each partition before the final reduction.

Reported consequences:
- mean error changes with M / split factor;
- the same row can change when evaluated alone vs in a larger batch;
- in one Qwen3-4B 4-bit decision-model test a probability reportedly changed from 0.12 alone to 0.38 in a batch.

This is not a Flash-Next quality result. It is a **reproducibility warning** for Project-51 MLX experiments.

Add to certified MLX A/Bs:
1. pin MLX version;
2. record batch/row shape;
3. compare single-row vs batched execution for identical tokens;
4. do not attribute a trajectory/logit difference to a quant or KV change until batch-shape arithmetic is controlled.

## NEW — oMLX #4202: M2 Ultra custom-FP16 v0.7.0 lane shows more MTP parking

Issue:
https://github.com/jundot/omlx/issues/4202

This is explicitly a custom FP16 port, not pristine oMLX.

Three-run medians from the report:
- 32K decode: 31.8 -> 28.7 TG (-9.7%);
- 64K decode: 30.8 -> 27.5 TG (-10.7%);
- MTP parking: **0/12 -> 9/12** requests.

The report lists multiple confounders and does not isolate an upstream regression.

Project-51 implication:
- no dual-M1 numerical target change;
- keep **MTP engaged/parked state, acceptance and verify-cycle time** as first-class metrics;
- pin exact runtime revision for Apple performance comparisons.

## UPDATE — mlx-serve #687 sharpens the cold-PLE/table-residency lesson

PR:
https://github.com/ddalcu/mlx-serve/pull/687

Created before this boundary, updated during it.

The open PR calibrates serial vs pooled reads for cold Qwen3.8 Flash-Next n-gram tables. Its earlier warming-disabled diagnostic reports 69-79% lower TTFT and much higher PP on an M5 Max when the table is almost entirely nonresident.

The author now explicitly says the proper default-warming main-vs-branch benchmark is still pending.

Project-51 conclusion is therefore methodological, not numerical:
- record PLE/table residency;
- separate cold-table startup from warmed steady state;
- do not transplant the large diagnostic percentages to oMLX/Strata or the M1 cluster.

## SAME-DAY CURRENT — Strata baseline remains v0.1.35

Release page still lists **v0.1.35 as latest** at this cutoff:
https://github.com/Niko1221/Strata/releases/tag/v0.1.35

No v0.1.36 release appeared in the window.

## Strict-window negatives / no target movement

Searched through the cutoff:
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
- Ishizuki;
- broader Qwen3.8-Flash-Next GitHub reports.

No strict-window evidence changes:
- the high-GQA K-precision decision;
- the stock-Strata-before-TurboQuant order;
- IQ3_S as the primary target;
- native 262,144 as production context;
- the current IQ3_S TG/PP planning centers;
- the decision not to buy another GPU or 128 GB RAM before exact-box measurements.

No new TurboQuant change supersedes Q8/INT8 K + compressed V as the custom-KV direction if stock Strata eventually needs it.
No new DASLab long-agent quality table appeared.
No new Ishizuki item changes the plan.
No SGLang update in this window changes the already-recovered replay/fold GDN idea.
No TensorFold item in this window changes the dual-M1 canonical targets.

## Exact-box qualification delta

Add/clarify these checks:

1. **PCIe calibration sanity**
   - log startup probe on multiple fresh starts;
   - if unstable, run calibrate and pin `pcie_frac`.

2. **Late-allocation gate**
   - capture transient VRAM through a real 250K-ish cold prompt;
   - boot/idle fit does not count.

3. **Restore-pressure soak**
   - prefix restore/reuse + MTP + near-full memory + immediate decode in the same scenario.

4. **MLX batch-shape determinism**
   - same prompt/tokens alone vs batched;
   - same revision and kernel path.

5. **MTP controller telemetry**
   - offered/accepted drafts;
   - engaged vs parked time;
   - verify-cycle cost.

## Target state

Unchanged:
1. Strata baseline: **v0.1.35**.
2. IQ3_S/native262K physical-fit prior on 5070-Ti-16GB / 64 GB: **~90%**.
3. Windows auto-admission: **~85%**.
4. 8 h zero-stall soak: **~75%**.
5. 24 h zero-stall soak: **~55%**.
6. Built-in restart/recovery <60 s: **~55%**.
7. Mature IQ3_S TG/PP centers: **unchanged**.
8. Production context target: **262,144 native**.
9. No hardware purchase before exact-box data.

## New hard boundary

**2026-10-02 12:27:00 UTC**
