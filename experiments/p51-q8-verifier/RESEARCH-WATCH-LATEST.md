# Project 51 research watch — 2026-10-04 18:06 ET

Freshness boundary entering: **2026-10-04 21:01:52 UTC**
Cutoff: **2026-10-04 22:06:41 UTC**

## Decision

**No headline TG/PP target movement and no Flash fit/admission/stability-prior movement.**

This pass hardens qualification in four places:

1. Strata #838 closes two remaining q8_1 fused-quantizer overflow paths associated with the repeated-token-collapse
   family. It is a strong candidate fix, not a proven root cause. Exact-box soak should use the clamp or a later build
   containing it.
2. Strata #840 shows Windows/HIP `--calibrate` can measure ~18x slower than the actual server path. Project-51 AMD
   tuning must use server-path A/B runs until calibration parity is demonstrated.
3. Strata #843 shows **empty assistant turns poison later Qwen tool use**. Agent qualification now includes empty-turn
   history contamination and records runtime/history normalization separately from native model success.
4. Strata #783 gains a deep-context receipt: +14% decode at 119K and +9.5% at 238K on one RTX4090, with prefill flat.
   This raises priority of an exact 5070/IQ3_S A/B but gives no numeric transfer.

The strict hard boundary advances to **2026-10-04 22:06:41 UTC**.

## NEW — Strata #838: complete q8_1 finite clamp for fused SwiGLU paths

PR:
https://github.com/Niko1221/Strata/pull/838

Created **2026-10-04 21:10:31 UTC**.

0.1.39 had already clamped two q8_1 activation quantizers so fp16 scale/sum fields remain finite, but two fused paths
still wrote raw q8_1 block metadata:

- `native_swiglu_quantize_q8_1_kernel`: shared expert decode + multi-token path, default enabled;
- `native_gu_fused_kernel`: routed expert fused gate/up on gfx906 EXP_MODE=8.

#838 routes both through the same finite clamp.

RTX5090/sm_120 synthetic test:
- 237 already-finite blocks remain bit-identical;
- 3 overflow cases clamp finite on all three tested quantizer paths;
- patched path: 0 failures;
- old fused SwiGLU path: 4 failures in the added overflow test.

The author also reports a separate Flash-Next conversation on a 5090 fork collapsing to token 0 / "!" around 99K
positions and persisting when that history was reused, but could not reproduce or causally tie it to this kernel.

Project-51:
- classify #838 as a **high-priority stability patch candidate**, not a proven #606 root cause;
- exact 5070/64GB soak should include:
  - finite-activation instrumentation/canary;
  - repeated-token collapse breaker/telemetry;
  - long sampled xhigh output around 100K+;
  - clean restart/replay control;
- no 8h/24h prior movement yet.

## NEW — Strata #840: Windows/HIP calibration path is not trustworthy

Issue:
https://github.com/Niko1221/Strata/issues/840

Created **2026-10-04 21:14:19 UTC**.

RX7900XTX / Windows / HIP prebuilt 0.1.39 / IQ2_XS:
- `--calibrate`: ~4 TG and ~7 PP on tiny prompts;
- same engine/config via normal `server.py`: ~74-78 TG short and ~66 TG after 82.9K, with ~100+ PP on tiny prompt and
  ~332 PP on a 984-token uncached append;
- draft acceptance remains normal.

The calibration path is therefore measuring a radically different launch/runtime regime and choosing knobs from noise.

Project-51 AMD rule:
- **do not use `--calibrate` on Windows/HIP as evidence** until server-path parity is demonstrated;
- RX6800 sweeps use one-server-per-arm A/B for pool workers / pcie-frac / spec settings;
- retain engine/config/launch identity in every result.

This does not transfer numerically from gfx1100 to gfx1030.

## NEW — Strata #843: empty assistant turns can suppress future tool calls

Issue:
https://github.com/Niko1221/Strata/issues/843

Created **2026-10-04 21:29:09 UTC**.

Observed with Qwen IQ3_S and Swift IQ3_XXS in agent sessions:
- a previous assistant turn with empty content and no tool call can become an imitation pattern;
- later requests close reasoning and emit no tool call at all;
- parser is not at fault because the model never writes the call.

Reported 20-run cells:
- fresh request: 20/20 tool behavior;
- contaminated history with 3 empty assistant turns: as low as 0/20 at T=0.3;
- skip empty assistant turns while rendering history: **20/20** on tested Swift and Qwen arms.

Project-51 agent gate adds:
- explicit empty-assistant-turn history contamination fixture;
- record native empty-turn rate;
- history normalization/filtering is an **adaptation-assisted** lane, not native-model success;
- parser recovery, history normalization and native tool success remain separate labels.

This is distinct from #804, where the model writes a tool call inside an unclosed thinking span.

## NEW — Strata #845: batch path now honors all-resident stages

PR:
https://github.com/Niko1221/Strata/pull/845

Created **2026-10-04 22:03:49 UTC**.

Combining layer split + batch/parallel >=2 could wait forever for host doorbells on a fully resident stage, because the
all-resident path intentionally does not ring them.

Fix mirrors the solo fast path in `run_slot_rows` / `batch_poll`.

RTX5090 + RTX3090, split 36, batch 2-3:
- 3 concurrent requests complete;
- zero "never rang" failures;
- batch windows average ~1.9 rows;
- server parallel test suite: 11 pass.

Project-51:
- useful multi-agent/layer-split correctness fix;
- no single-request target credit;
- include all-resident-stage + parallel>=2 in any future Strata multi-agent gate.

## UPDATE — Strata #783 deep-context CUDA fusion benefit is larger than short-context benefit

New comment **2026-10-04 21:42:50 UTC**.

Single RTX4090 / Flash IQ2_XS / 262K / q4_0 / resident experts:

- 119K decode:
  - v0.1.39 ~106.2-106.6 TG;
  - +#783 ~121.5-121.8 TG;
  - **~+14%**.
- 238K decode:
  - v0.1.39 ~126.7-127.3 TG;
  - +#783 ~138.9-139.3 TG;
  - **~+9.5%**.
- prompt reading remains essentially unchanged (~4.0K PP);
- recall correct in every reported run.

Project-51:
- #783 becomes an even higher-priority exact RTX5070/IQ3_S A/B;
- the earlier partial-residency end-to-end divergence history still prevents production speed credit until exact-target
  trajectory/quality controls pass.

## NEW — Strata #844: UD-Q3_K_XL quality/speed comparison against GSQ-RCO IQ3_S

PR:
https://github.com/Niko1221/Strata/pull/844

Created **2026-10-04 21:42:39 UTC**.

Despite its filename, the expert formats are largely IQ3_XXS / IQ4_NL, with Q8 dense-side tensors.

On a RTX3060 + RTX5070Ti split:
- teacher-forced same-next-token vs official Qwen API: **93.0%** for both GSQ-RCO IQ3_S and UD-Q3_K_XL;
- 5-token KL: **0.0536 IQ3_S vs 0.0519 UD-Q3_K_XL**;
- six trap/code questions x2 seeds: 12/12 both;
- 100K-start agent-like writing: **77.9 TG IQ3_S vs 56.6 UD-Q3_K_XL**;
- 100K start read: **61.6 s IQ3_S vs 81.8 s UD-Q3_K_XL**.

Project-51:
- interesting quality comparator, but it is larger/slower and does not displace GSQ-RCO IQ3_S;
- no target movement.

## NEW — gfx900 experimental port (#839)

Strata #839 adds a Vega10/gfx900 experimental Linux path with wave64 validation and basic live server coverage.
Useful portability work; no Project-51 hardware transfer.

## CURRENT PUBLIC ARTIFACT CHECK

Swift 1.5 Flash-Next public GSQ-RCO remains:
- IQ3_XXS ~75.97 GB;
- IQ2_XS ~68.15 GB;
- Q2_0 experimental ~66.55 GB;
- **no IQ3_S**.

ThinkingCap Qwen3.8-27B remains public as BF16/model weights, but no public ThinkingCap-specific GSQ-RCO IQ3_S release
was found at cutoff.

Swift 1.5 Qwen3.8-27B GSQ-RCO IQ3_S+MTP remains the preferred first alternate dense artifact.

## KNOWN / NO CHANGE

- One-time 5070 cold-prefill -> M1 ownership handoff remains the formal dense-27B fleet topology.
- Flash production baseline remains DASLab GSQ-RCO IQ3_S.
- Swift Flash IQ3_S remains the highest-priority Flash challenger to build/qualify.
- 5070-Ti Flash physical fit remains ~97%.
- Windows 16-GB/64-GB full-context admission remains ~90%.
- 8 h / 24 h zero-stall remains ~75% / ~55%.
- Dual-M1 Flash production remains native262K >=35 TG / >=400 cold PP.
- Dual-M1 Flash performance remains ~128K >=40 TG / >=425 cold PP.
- Dense-27B RTX5070 mature ladder remains unchanged.
