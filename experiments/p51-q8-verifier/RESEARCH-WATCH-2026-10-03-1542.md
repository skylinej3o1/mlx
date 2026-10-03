# Project 51 research watch — 2026-10-03 15:42 ET

Freshness boundary entering: **2026-10-03 11:53:50 UTC**
Cutoff: **2026-10-03 19:42:13 UTC**

## Decision

**No numeric fit/admission/stability/TG/PP target movement.**

Primary Windows state remains:
- Strata baseline: **0.1.38**;
- IQ3_S + native262K physical fit/admission: **~95%**;
- Windows 16-GB/64-GB full-context admission: **~90%**;
- 8 h / 24 h zero-stall: **~75% / ~55%**;
- #481-style automatic containment/no-manual-service-restart: **~85%**;
- native production context: **262,144**, with **204,800** first fallback;
- conversation parking OFF for initial certification;
- explicit `reasoning_budget_tokens` for high/xhigh;
- frozen residency for source/AA qualification.

This pass makes five durable implementation/qualification changes:

1. **Do not credit Strata #646's +39-72% headline to the 5070-Ti lane.**
   A fresh RTX 5080 16-GB partially-resident test—the closest public regime to the user's 5070 Ti—crashes 3/3 with
   `--spec 4` in the new IQ3_S staged-codebook path. With the crash worked around, the branch is not faster than main
   and is modestly slower in matched high-acceptance comparisons. A separate 2x3090 IQ3_S run sees ~11-14% decode
   gain but fails bit-exact source gates. Keep #646 out of the certified baseline until the non-resident path is fixed.

2. **Streamed KV is part of the certified 16-GB Blackwell configuration.**
   Strata #620 shows an exact 5060 Ti 16 GB / 64 GB / IQ3_S system can OOM during startup with the full 131K INT8 KV
   resident in VRAM, yet starts cleanly after adding `--kv-resident 32768`. For Project 51, `--kv int8
   --kv-resident 32768` (or an explicitly measured equivalent) is now a baseline requirement rather than a tuning
   option.

3. **RX6800 producer proof starts prefill-only, with speculation off.**
   Strata #649 reports an intermittent gfx1030 verify hang on RX6950XT / UD-Q4_K_XL that appears specifically in
   speculative verify at full-attention layers. This does not invalidate RX6800 as a **prefill appliance**; it argues
   that the first dense-27B producer POC should measure target-only cold PP/state export with no MTP/spec decode.

4. **Single-row DeltaNet micro-tuning is not the first custom-M1 lever.**
   TensorFold #323 gets only ~0.8-2.2% full-model decode uplift from exact M2-Max Qwen3.8-27B DeltaNet one-row
   geometry, despite 6-14% isolated projection wins. This strengthens the existing priority: bespoke work goes first
   into long-context multi-row verification/state/cache machinery, not GDN one-row microkernels.

5. **Disk session files become a distinct persistence candidate, separate from conversation parking.**
   Strata #668 restores a 63K conversation in ~1.05 s versus ~25.5 s re-prefill on RTX4070Ti and reports the same next
   32 token IDs. Initial production still keeps conversation parking OFF; session files are a future persistence arm
   that must qualify at 128/200/250K and prove restart/failure/corruption semantics.

No newer Strata release than **0.1.38**.

## UPDATE — Strata #646: headline resident-GPU speedup does not transfer to a 16-GB partial-residency lane

PR:
https://github.com/Niko1221/Strata/pull/646

Original headline:
- dual RTX3090, fully resident Swift IQ2_XS;
- 256K K8V4, spec4;
- +39-72% decode depending workload;
- claimed bit-exact tokens/acceptance.

### New RTX5080 16-GB partial-resident result

Independent Windows test:
- RTX 5080 16 GB, sm_120;
- Swift IQ3_XXS;
- only ~21.5% of experts resident, ~81% lookup hit;
- 131K context, spec4.

Blocking correctness failure:
- branch crashes **3/3** with `--spec 4`;
- baseline main: 0/3 crashes;
- `--spec 1` clean, `--spec 2` already faults;
- bisection points to staged **IQ3_S codebook** reads in the new multi-token expert path;
- `STRATA_OLD_IQ_MMVQ=1` or de-staging IQ3_S avoids the crash.

Performance with IQ3_S staging worked around:
- baseline mean decode: **160.5 TG**;
- PR mean: **136.2 TG**;
- high-acceptance paired comparisons: roughly **-5 to -8%**;
- prefill ~251 -> 243 PP in that run.

The zero-doorbell resident verify graph never runs because `all_resident_` is false.

### Separate 2x3090 IQ3_S result

Another independent Linux run:
- 2x RTX3090, IQ3_S, peer-device tier, 262K INT8;
- decode gains roughly **+11 to +14%** at 8/32/128K;
- ~+7% on a 3K story.

But exactness gate:
- 2/3 short greedy prompts diverge from the stock 0.1.38 reference;
- 20K long gate fails;
- divergence survives `STRATA_OLD_IQ_MMVQ=1`, implicating other changed arithmetic/order.

Project-51 decision:
- **#646 receives zero planning credit on the single-5070Ti lane**;
- do not cherry-pick it into source/AA certification;
- revisit only after non-resident sm_120 crash is fixed and exact IQ3_S parity/quality is independently requalified.

## NEW — Strata #620: exact 16-GB Blackwell/64-GB host proves full resident KV can consume startup headroom

Issue:
https://github.com/Niko1221/Strata/issues/620

Environment:
- RTX 5060 Ti 16 GB, sm_120;
- i5-14600K;
- 64 GB host RAM;
- Strata 0.1.38 release;
- IQ3_S;
- 131,072 context, INT8 KV;
- desktop on iGPU, dGPU otherwise empty.

Without `--kv-resident`:
- entire 131K KV stays in VRAM;
- startup reaches expert-arena load then fails:
  **`native head upload: out of memory`**.

Adding:
- `--kv-resident 32768`

frees roughly ~2 GB VRAM and startup succeeds:
- Q5_K head uploads;
- expert cache ~7.23 GiB;
- ~514 MiB VRAM free after load.

This is not evidence against the Project-51 target because our baseline already streams long-context KV.
It makes the requirement explicit:
- certify 5070Ti with **INT8 streamed KV, resident window ~32K first**;
- do not run native262K with all KV resident;
- preserve meaningful post-load VRAM reserve; “more nominally free before setup” is irrelevant if planning spends it
  before the head/transient allocations land.

## NEW — Strata #674: IQ3_S native262K can be very fast even on an old dual-Xeon host with enough GPU/RAM

PR:
https://github.com/Niko1221/Strata/pull/674

Community report:
- RTX3090 Ti 24 GB, PCIe3 x16;
- 2x Xeon E5-2699 v3;
- 384 GB DDR4-2133;
- Ubuntu;
- original GSQ-RCO IQ3_S;
- 262,144 context, INT8 streamed KV;
- ~15 GiB experts in VRAM.

Warm/calibrated:
- decode **~94.9 TG** on the kept NUMA placement;
- 93.7-95.9 band;
- ~1,304 PP on a ~5K prompt;
- real agent traffic 56-80 TG.

This strongly confirms that IQ3_S/262K itself is not an inherently slow regime and that a high expert-cache hit can
hide an old CPU/PCIe3 host.

It does **not** strengthen the 64-GB host admission prior because the box has 384 GB RAM, nor does the 24-GB-card
decode rate transfer to 5070Ti16.

## NEW — Strata #618: Windows HIP remains healthy to ~248K on a much stronger AMD card

PR:
https://github.com/Niko1221/Strata/pull/618

R9700 32 GB / Ryzen9950X / ~61.5GB host / Windows / IQ2_XS / 0.1.38:
- 4K: ~856 PP / 99.8 TG;
- 33K: ~1,182 PP / 97.8 TG;
- 131K: ~1,232 PP / 89.9 TG;
- **248K: ~1,130 PP / 87.5 TG**;
- 6/6 needles at ~33K/~131K;
- all measured requests completed.

This is far stronger than the RX6800 and a different model/quant, so do not transfer the numbers.
It does prove the Windows HIP long-context engine path itself can scale deep when the hardware/runtime are suitable.

For the RX6800 dense producer, this remains architecture confidence only.

## NEW — Strata #649: gfx1030 speculative verify can intermittently hang

Issue:
https://github.com/Niko1221/Strata/issues/649

RX6950XT / gfx1030 / ROCm7.1 / Strata 0.1.37 + current-main:
- UD-Q4_K_XL;
- 31 GB host;
- spec2;
- 7-12 GiB resident expert budget.

Failure:
- intermittent `verify: timed out at layer N`;
- always a full-attention layer;
- warm-page-cache/faster runs appear more vulnerable;
- 12-GiB budget hung 2/2; ~7-GiB roughly 1-in-3;
- sync-every-layer and adaptive-nowait controls did not fix it.

Maintainer suspects CPU-pool / GPU-wait handshake on HIP.

Project-51 consequence:
- **do not use Strata/gfx1030 speculative decode as the first RX6800 producer path**;
- RX producer POC is target-only **cold prefill + state export**, spec/MTP off;
- this issue does not reduce the value of RX6800 as a prefill appliance because verify/decode can be omitted entirely.

## NEW — TensorFold #323: exact M2-Max DeltaNet one-row tuning gives only a small full-model gain

PR:
https://github.com/ashhart/TensorFold/pull/323

M2 Max 64 GB / Qwen3.8-27B MLX 4-bit:
- exact one-row DeltaNet input projection: **-6% latency**;
- output projection: **-13.5%**;
- recurrence itself ~unchanged.

Full model, 32-token short-context decode:
- prompt 1: **1.022x** throughput;
- prompt 2: **1.008x**;
- tokens, final logits and cache-state bits matched.

Not tested:
- M1 Max;
- long context;
- drafted decode.

Project-51 consequence:
- nice upstream/cherry-pick candidate if it later generalizes to M1;
- **not a reason to spend custom-engine effort here first**;
- long-context multi-row GQA verification remains the high-leverage bespoke target.

## NEW — Strata #668: disk session save/restore is a promising alternative persistence lane

PR:
https://github.com/Niko1221/Strata/pull/668

Opt-in session file:
- saves complete conversation state to disk;
- restores after restart of the same engine version/model/settings;
- validates model/config fingerprints and hashes before device writes;
- streams KV in 16-MiB blocks instead of making a full host copy;
- only slot 0; refuses layer split/peer-device/prompt-cache0.

RTX4070Ti, ~63K conversation:
- restore: **1.05 s** after model loaded;
- re-prefill: **25.5 s**;
- next continuation: same **32 token IDs** as the non-restart path.

Project-51 decision:
- keep live conversation parking **OFF** in the initial production baseline;
- add session-file restore as a **separate persistence candidate**;
- promotion requires 128K -> 200K -> ~250K restore, state-hash/continuation parity, damaged-file refusal, low-RAM
  preflight and total disk/restore latency measurements.

## NEW — Strata #652: final speculative window can commit tokens the client never saw

PR:
https://github.com/Niko1221/Strata/pull/652

Current behavior:
- verify commits all accepted positions;
- API returns only outputs before `max_tokens` / first end-of-turn;
- the live session can therefore contain accepted draft tokens that were never sent to the client;
- next full-history turn no longer matches live state and falls back to an earlier checkpoint/re-prefill.

Eight-turn coding conversation:
- main resumed 5/7 follow-ups;
- branch resumed **7/7**;
- misses on main were max-token cuts inside a verify window.

Project-51 agent-state gate:
- committed state must equal **exactly the token sequence exposed to the client**;
- max-token and end-of-turn inside a multi-row verify window become explicit resume tests;
- this is agent-state correctness/performance, not a TG target change.

## NEW — Strata #656: safe-boundary prefill preemption is promising for multi-agent service

PR:
https://github.com/Niko1221/Strata/pull/656

Opt-in, single-GPU:
- long prefill can suspend after a completed chunk;
- snapshot includes running state, QSA positional/KV/pooled state and drafter KV;
- short queued request runs;
- long request restores and continues.

RTX4070Ti SUPER / IQ3_XXS:
- short request queue wait behind 50K prefill: **40.5 -> 2.9 s (-93%)**;
- interrupted request total wall: 43.8 -> 45.3 s (**+3.4%**);
- reported full state fingerprint and tokens identical at tested boundaries.

This is highly relevant to future multi-agent serving, but remains open/opt-in and snapshots consume RAM.
Do not put it in the first certified baseline; track as a scheduler feature after B1 correctness/stability.

## UPDATE — TurboQuant #392 materially improves deep-spill CUDA, but does not change protected-K policy

PR:
https://github.com/TheTom/llama-cpp-turboquant/pull/392

Deep-spill RTX4090-Laptop 16GB / Qwen3.8-27B:
- q8 K / turbo3 V at 180K: ~700 PP / **18.3 TG**;
- q8 K / turbo4 V: ~699 PP / **16.6 TG**;
- turbo4 K / turbo3 V: **30.3 TG** after the updated native routing path.

Earlier 233K deep-spill turbo3 path improved roughly:
- 2.42 -> 8.13 TG with native routing/width gate;
- -> **11.0-11.7 TG** with batched H2D.

Project-51 interpretation:
- impressive streamed-KV engineering;
- **does not overturn our protected-K production order**.
  Q8/INT8 K + Turbo4 V and then Q8/INT8 K + Turbo3 V remain the aggressive capacity arms;
- turbo-compressed K is still a research-only lane because Qwen high-GQA K sensitivity remains the stronger quality
  concern.

## UPDATE — mlx-serve hybrid SSD restore shows why restore boundaries need one-token-forward semantics

PR:
https://github.com/ddalcu/mlx-serve/pull/714

A hybrid-state SSD cache restored a checkpoint exactly at the prompt's final token and then crashed.
The fix skips that terminal checkpoint, leaving the last token to pass through a normal forward.

Before:
- 1,610/1,610 tokens restored;
- segmentation fault.

After:
- cold/earlier-checkpoint fallback;
- HTTP 200 and normal generation.

Project-51 consequence:
- restore boundary certification must include **checkpoint exactly at prompt end**;
- safe restore may intentionally leave one token to forward to re-establish recurrent/hybrid state invariants.

## Strict-window negatives

Searched:
- Strata;
- oMLX;
- TensorFold;
- MTPLX;
- Splash;
- Ishizuki;
- llama.cpp;
- SGLang;
- vLLM;
- MLX;
- TurboQuant;
- mlx-serve;
- DASLab/Hugging Face;
- ByteShape/public sources.

Strata main still declares **0.1.38**.
No strict-window MLX-core change.
No strict-window Splash/Ishizuki change.
No new exact M1 Max 64-GB DASLab/ByteShape benchmark.
No new exact single-RX6800 dense-Qwen3.8-27B PP receipt.
No hardware-purchase evidence.

## Target state after this pass

1. Primary Windows baseline: **Strata 0.1.38**.
2. IQ3_S/native262K physical fit: **~95%**.
3. Windows 16GB/64GB admission: **~90%**.
4. 8 h / 24 h zero-stall: **~75% / ~55%**.
5. #481 automatic containment: **~85%**.
6. Native target 262144; 204800 first fallback.
7. Exact 16-GB Blackwell baseline requires **INT8 streamed KV with ~32K resident window first** plus real VRAM reserve.
8. Strata #646 is **excluded** from 5070Ti certification/planning until non-resident sm_120 correctness is fixed.
9. High/xhigh: explicit reasoning budget.
10. PLE ladder unchanged: IQ4_NL -> FP8 candidate -> BF16 exact control.
11. Single-M1 27B remains **25 TG / 110 cold PP**.
12. M1 bespoke priority remains long-context multi-row verifier/state lifecycle; not single-row DeltaNet micro-tuning.
13. RX6800 producer first POC: **target-only prefill, speculation off**, then state export/import.
14. Primary dense artifact remains DASLab IQ3_S-MTP for production-like runs, target-only IQ3_S for no-draft producer control.
15. Conversation parking remains OFF initially; **disk session-file restore** becomes a later persistence candidate.
16. Agent-state certification adds “commit only client-visible outputs” at max-token/end-turn verify boundaries.
17. Turbo aggressive-K order unchanged: protected INT8/Q8 K before any turbo-K research.
18. No hardware purchase change.

## New hard boundary

**2026-10-03 19:42:13 UTC**
