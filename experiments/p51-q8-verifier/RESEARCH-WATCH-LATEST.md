# Project 51 research watch — 2026-10-02 12:59 ET

Freshness boundary entering: **2026-10-02 14:24:02 UTC**
Cutoff: **2026-10-02 16:59:41 UTC**

## Decision

This pass **does change one planning prior**.

The physical-fit/admission case for the user's **RTX 5070 Ti 16 GB + 64 GB Windows + IQ3_S + native 262,144**
lane is now strong enough to raise from **~90% to ~95%**.

The key evidence is a recovered Strata #406 comment from a **Windows / 64 GB RAM / 16 GB VRAM / IQ3_S** user:
setup had conservatively capped the context, but manually setting 256K worked fine with only a slight performance hit.
The original #406 reporter also ran IQ3_S at full native context on a 64-GB Linux host and reported >6 GB free RAM.
Strata 0.1.33 subsequently changed setup to preserve an explicitly requested 262,144 context instead of forcing 128K.

This is not the user's exact GPU model, so it is not 100% certification. It closes most of the remaining **host-memory
shape** uncertainty, however, when combined with:
- exact RTX 5070 Ti 16 GB / ~63 GB Windows / native262K operation on IQ3_XXS (#31);
- IQ3_S through a real ~250K prompt on only 11 GB VRAM (#469);
- exact RTX 5070 Ti near-native 257,466-token cold prompt execution on IQ3_XXS (#200).

Windows full-context admission planning confidence moves from **~85% to ~90%**.

The 8 h / 24 h **zero-stall** priors do **not** move in this pass: Strata #481 remains open on 0.1.35.
The maintainer has now resolved the wait site well enough to add automatic restart behavior to the **next release**,
but that release and its soak receipt do not yet exist at this cutoff.

No TG/PP center changes. No hardware purchase. Native262K remains the production target.

## RECOVERED OLDER EVIDENCE — Strata #406 materially strengthens 64-GB IQ3_S fit

Issue:
https://github.com/Niko1221/Strata/issues/406

Original report:
- IQ3_S;
- Ubuntu;
- 64 GB host RAM;
- manual full 256K/native context;
- >6 GB RAM still free at full context;
- only ~1.8 GB extra was needed for 256K versus 128K in that setup.

More important for the user's topology, a commenter reports:
- **Windows**;
- **64 GB RAM**;
- **16 GB VRAM**;
- **IQ3_S**;
- setup capped 128K;
- manually setting **256K worked fine**, with only a slight performance hit.

Maintainer response:
- multiple users had reported the same;
- setup should recommend, not force;
- released in **0.1.33**, preserving an explicitly selected 262,144 context with a warning.

Interpretation:
- this is not an exact RTX 5070-Ti receipt;
- it **is** the previously missing same-OS / same-host-RAM / same-VRAM-capacity / same-quant memory-shape receipt;
- together with #469 and #31/#200, physical fit is now a high-confidence proposition rather than a borderline estimate.

New Project-51 physical-fit prior: **~95%**.

## UPDATE — Strata #481: deadlock recovery path identified for the next release

Issue:
https://github.com/Niko1221/Strata/issues/481

The maintainer resolved the supplied stack against the 0.1.34/0.1.35 lineage:
- the engine main thread is in the STL's untimed condition-variable wait;
- the likely state is engine waiting for its next command while the server is waiting for the current request to end;
- the two sides have lost step;
- the current stall watchdog only counts while the engine considers a request running, so this path escapes it.

The maintainer says the **next release** changes the server behavior:
- no engine output for too long during a request, or
- a stop request that is never acknowledged
will cause the engine to restart instead of waiting forever.

This is materially encouraging for production usability, but it is **not yet released-and-soaked evidence**.
Therefore:
- 8 h zero-stall prior stays ~75%;
- 24 h zero-stall prior stays ~55%;
- built-in <60 s recovery stays ~55% for the current 0.1.35 baseline;
- re-score recovery immediately when the next release lands and has an exact/near-exact soak.

## UPDATE — Strata #500: independent hardware result rejects the giant universal-speedup interpretation

PR:
https://github.com/Niko1221/Strata/pull/500

An independent RX 7900 XTX 24 GB / Ryzen 9 7900X / IQ3_S test reports:
- decode: **60.2 vs 61.3 tok/s**, about **-2.3%** for #500;
- 32K prefill: about **-0.6% median**, confidence interval spanning both directions.

The tester's interpretation matches the mechanism:
- on small verify windows, the quant work is only microseconds;
- the new pool phase's fixed publish/wake/done overhead can exceed the serialized work it removes;
- the patch may still pay in regimes with many more expert-token quant jobs or CPUs with a different overhead balance.

This means:
- the source-level serial barrier is real;
- the original +69-78% end-to-end result is **not a portable Project-51 speed prior**;
- keep #500 out of canonical TG centers unless the exact 5070-Ti/Ultra-7 box measures a win.

## NEW — Strata #512: QSA active-bound optimization is explicitly *not* for the 5070 Ti

PR:
https://github.com/Niko1221/Strata/pull/512

On a modified 2080 Ti 22 GB at ~131K actual context inside a 262K allocation:
- fresh prefill: **~831 -> ~886 tok/s**, +6.83%;
- TTFT saves ~10 s.

But the patch is intentionally enabled **only on sm_75**.
The author notes the RTX 5070 path retains the allocated-capacity rule because active-bound selection regressed it
by roughly 1-3% in current source testing.

No target-GPU transfer.

## NEW — Strata #508: another native262K 16-GB-class operational receipt

PR:
https://github.com/Niko1221/Strata/pull/508

Setup:
- 2x RTX 5060 Ti 16 GB;
- Xeon E5-2690 v4;
- 125 GB RAM;
- IQ3_XXS;
- Strata 0.1.35;
- configured 262,144 context;
- INT8 KV + MTP.

Fresh measurements:
- 4K: 808 PP / 77.5 TG;
- 32K: 1,931 PP / 72.7 TG;
- 128K: 2,199 PP / 72.4 TG;
- 32K/128K needle: 6/6 exact.

Different topology and host size, so no exact-box target movement.

## NEW — Strata #510: interrupted tool-call histories no longer need to poison an agent session

PR:
https://github.com/Niko1221/Strata/pull/510

Current frontend can throw an unhandled JSON parse error when an agent client sends history containing a partial or
malformed tool-call argument. Because clients preserve history, every subsequent request can then fail with HTTP 400.

The open patch:
- falls back to a raw argument payload instead of rejecting the session;
- logs the parse failure;
- adds a regression test.

This is directly relevant to the user's coding-agent workload. Track for merge/release; no throughput effect.

## NEW — Strata #511: very-tight-VRAM long-run failure is a useful edge case, not a target-box analog

Issue:
https://github.com/Niko1221/Strata/issues/511

RTX 3070 Ti, IQ3_S, 0.1.35 reaches:
- 0 MiB VRAM free after load;
- long multi-turn operation;
- eventually a verify timeout at layer 31 after very long generations.

The target 5070 Ti has 16 GB and Project 51 explicitly requires reserve/headroom gates, so this does not lower the
~95% physical-fit prior. It reinforces that **idle fit at zero reserve is not admission**.

## NEW — oMLX #4209: 4-bit Flash-Next MTP is not automatically greedy-exact

Issue:
https://github.com/jundot/omlx/issues/4209

On one M5 Ultra / oMLX 0.7.0:
- a uniform 4-bit Qwen3.8-Flash-Next checkpoint produced different greedy output with Lightning MTP on vs off on all
  four coding prompts;
- the 5-bit checkpoint was byte-identical on the same prompts;
- 4-bit MTP output was stable across repeated runs, but differed from one-token decode.

This is Apple/oMLX evidence, not Strata evidence.
It does strengthen the Project-51 rule that low-bit production certification must test **plain decode vs MTP**
on the exact quant/runtime, not infer correctness from plausible output or benchmark score.

## NEW — oMLX #4210: M1 Max / 64 GB Flash-Next expert staging gives a small real decode win

PR:
https://github.com/jundot/omlx/pull/4210

Exact M1 Max 64 GiB, Flash-Next oQ4e, 25% resident / 75% streamed experts, MTP off:
- 1K input: +7.55% decode;
- 4K: +5.24%;
- 8K: +5.04%;
- all 15 A/B pairs positive.

The change removes Python-bytes copies by staging offloaded expert slabs through shared buffers.
The PR reports preserved token/probability/routes/read-plan behavior.

Useful single-M1 mechanism evidence, not a dual-M1/TB4 target move.

## NEW — TensorFold Flash-Next MTP and n-gram work

### #250 — measured-cost MTP stop

On one GB10, the opt-in cost-based draft stopping policy reports:
- MLX 4-bit geometric mean over 32 cases: **+4.3%**;
- EXL3 4.05 bpw: **+2.8%**;
- every drafted reply equals serial reference in the reported tests.

This supports per-engine measured MTP economics instead of a fixed depth, but does not transfer numerically to Strata.

### #252 / #254 — PLE/n-gram page residency is a first-order cold-path variable

TensorFold #252 reads future EXL3 PLE pages ahead and cuts cold 24K prompt time dramatically on one GB10 while keeping
outputs identical. #254 re-reads/pins the table after warm-up and reports new-reply decode gains of roughly 11-14%
on EXL3 4.05 when the table otherwise begins only partly resident.

Project-51 implication:
- continue separating cold-page-fault behavior from warm steady-state PP/TG;
- record PLE/table residency in any cross-runtime comparison.

## UPDATE — mlx-serve #687: warmed default path no longer supports the earlier giant cold-calibration story

PR:
https://github.com/ddalcu/mlx-serve/pull/687

A proper main-vs-branch M5 Max / 128 GiB / default-warmer-on replication is now posted.
The table was 100% resident by readiness on all boots and branch auto-policy returned to serial after warming.

Observed request-level deltas are sub-1% and explicitly not claimed as speedups.

This confirms the methodological lesson already in Project 51:
**cold table residency and warmed production behavior must be measured separately.**

## Strict-window negatives

Searched:
- Strata;
- oMLX;
- TensorFold;
- llama.cpp;
- SGLang;
- vLLM;
- MLX;
- DASLab/Hugging Face;
- TurboQuant;
- mlx-serve;
- Ishizuki.

No strict-window item changes:
- IQ3_S as the preferred quality-first Strata quant;
- native262K production target;
- no-new-GPU / no-128-GB-RAM-before-testing decision;
- protected-K TurboQuant policy;
- stock Strata INT8 -> K8V4 -> Q4/custom-capacity test order;
- mature IQ3_S TG/PP centers.

No new TurboQuant repo change.
No relevant Ishizuki change.
No new DASLab long-agent IQ3_S certification table.

## Target state after this pass

1. Strata baseline: **v0.1.35**.
2. Exact-box IQ3_S/native262K physical-fit/admission prior: **~95%**.
3. Windows 16-GB/64-GB full-context admission prior: **~90%**.
4. 8 h zero-stall soak: **~75%**.
5. 24 h zero-stall soak: **~55%**.
6. Built-in restart/recovery <60 s on the current release: **~55%**; next release is expected to improve this but is unqualified.
7. Mature IQ3_S TG/PP centers: **unchanged**.
8. Production context target: **262,144 native**.
9. No hardware purchase before exact-box data.
10. #500 speedup is **not** incorporated into planning centers.

## New hard boundary

**2026-10-02 16:59:41 UTC**
