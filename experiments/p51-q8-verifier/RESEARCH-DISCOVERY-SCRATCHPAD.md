# Project 51 — ranked research leads (Nov18 2026 10:11 EST)

Last hard cutoff 2026-11-18T15:11:40Z; [latest dated watch](./RESEARCH-WATCH-2026-11-18-1011.md). Score F owner exactness, N novelty, E evidence, A action, I independent, each0–3; weighted total 3F+2N+3E+2A+I. Scores are not probabilities.

## Ranked active leads
1. **Tool-call result ordering (28/33 F2N3E3A3I1)** [TensorFold #3832](https://github.com/ashhart/TensorFold/pull/3832) OPEN upstream patch fixes prior #3775, verify merge and ordered `tool_call_id` before template hash.
2. **Strata GSQ IQ3S source expert-cache regression (25/33 F2N3E2A3I1)** [#6208](https://github.com/Niko1221/Strata/issues/6208) two 3060 hosts ~55→34/40TG at same IQ3S as cache hit drops; needs profile routing bisect and independent original quant control, no owner run.
3. **Real GSQ coding agent + subagent choice (25/33 F2N3E2A3I1)** [#6213](https://github.com/Niko1221/Strata/issues/6213) two 34min offline Codex patch sessions QFN IQ3S on 2×4060Ti125GB; test human-verified tasks/hour and competent no-delegation.
4. **QFN original GSQ IQ3S long context AMD (22/33 F2N3E2A2I0)** [#6202](https://github.com/Niko1221/Strata/issues/6202) dual RX7800XT16+64GB host true127784 PP2494 TG56.4 drafted, no owner RX6800 nonXT+host16 equivalence.
5. **Basalt streamed KV SSD (22/33 F2N2E2A3I0)** [#382](https://github.com/jesdga95/basalt/pull/382) OPEN old PR updated Nov18, eight long session cache returns 10/16→16/16, other model/dualGPU, need exact restore+error gates.
6. **Strata persistent expert routing heat (24/33 F2N3E2A3I0)** [#6201](https://github.com/Niko1221/Strata/pull/6201) new open opt-in cross-task route memory and old multi-run speed, not neural/agent memory nor original GSQ fit.
7. **Qwen4 authentic Flash config (20/33 F3N1E1A3I0)** official Alibaba and Qwen model lists, exact main/PLE/MTP weights+active/total absent, old China/US rumors only.
8. **oMLX original GSQ external Splash CUDA bridge (25/33 F3N2E2A3I0)** oMLX0.8.0 native MLX partial layers, external original GGUF state handoff not demonstrated; avoid conflating.
9. **Paperniuk old M1 original GSQ (20/33 F3N1E1A3I0)** no new Paperniuk DS4/Splash commit; source128/259K exact and long soak resume unmeasured.
10. **Basalt body read/tool recovery (22/33 F2N2E2A3I0)** [#425](https://github.com/jesdga95/basalt/pull/425) 408 instead of permanently leaked thread, [#426](https://github.com/jesdga95/basalt/issues/426) not wired `tool_call_recovery`, agent correctness.
11. **M5 verifier tensor ops (17/33 F0N3E3A1I0)** [oMLX #5403](https://github.com/jundot/omlx/pull/5403) 128K ~185→157–164ms/step, excludes M1–M4, valuable architecture only.
12. **Dual M1 independent residency and TB4 (17/33 F2N2E1A2I1)** true source 259K ~57GiB each, must not treat as one128GB pool or extrapolate dualV100 NVLink.

## Deprioritized/closed
- **Qwen4-35B from Reddit on Nov18:** source linked Shuai Bai's **Nov16** social statement, not fresh model weights, no Flash parameters. Reopen on official manifests only.
- **Dual V100 UD IQ2_XS #6210:** below GSQXXS quality floor and different interconnect; cannot promote owner throughput.
- **M5-only oMLX #5401/#5403:** not old M1 path even when long-context benchmarks good.
- **RX7800XT x2 GSQ IQ3S:** original quant but two RDNA3 GPUs, larger RAM and draft; user RX6800 single host16 cannot infer performance.
- **Basalt #89** closed without GitHub merged flag this window; only source main commit can establish branch integration.
- **Basalt #382** authored Nov16, updated Nov18 not fresh whole measurement; watch future merge and independent ablation.
- **Direct source GSQxxs vs Unsloth UD-Q4KXL quality:** no same task benchmark; performance/resource comparisons are not preference proof.
- **oMLX0.8.0 native QFN oQh min70.8GiB:** cannot reside in 64GB M1 and below GSQ quality floor.
## Next exploration turn (max3)
1. Verify actual primary Qwen4 Flash manifests and Chinese release rumors vs recycled media; Paperniuk old M1.
2. Trace #6208 expert profile parsing/regression and #6201 proposed gated fix; compare with Basalt IQ3S cache and frozen owner conditions.
3. Follow #3832 tool-ID merge and #382 streaming-GDN/KV checkpoint restore correctness, real coding agents with exact task pass.
## Research debt
One-card owner RTX5070Ti16+64 host pristine historical GSQ IQ3S v2 32K INT8KV spec1 no draft not yet physically run; actual 2 M1Max64 original GSQXXS 128/259K speed gain not seen; source full CUDA prefill→M1 GDN+QSA+PLE state transfer not proven; trained Qwen4 Flash weights/spec absent. All owner downloads/tests require HIGH approval.