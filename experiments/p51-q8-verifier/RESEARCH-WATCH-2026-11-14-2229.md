# Project 51 research watch — November 14, 2026, 22:29 EST

Prior cutoff 2026-11-14T23:29:43Z; new cutoff 2026-11-15T03:29:48Z. Connected GitHub issues updated in window. Research-only; issue updates are not all new issues.

## High priority: Basalt 0.4.0 128K regression on RTX 5070 Ti (NEW)
[Basalt #366](https://github.com/jesdga95/basalt/issues/366), updated Nov15 01:05Z. Windows RTX5070Ti16+64GB RAM, QFN Unsloth UD-IQ3_XXS (NOT original GSQ IQ3_S), int8KV 131072 prompt, max-context133249, resident budget39GiB. Basalt0.3.3 TG conv107.9/struct169.1/prose112.2; Basalt0.4.0 budget39 85.5/81.2/81.2; budget38 110.3/171.6/111.7. Expert-cache hits ~75%→20-49%→~75%. Hypothesis: retained prefill lend region steals VRAM expert-cache slots; not code-proven. 0.4.0 16K unaffected. Preserve frozen first PC test original GSQ IQ3_S true32K int8KV one slot spec1 no draft. Do not transpose speed to our pack.

## High priority: RX6800 long-context reliability (UPDATED)
[Strata #5892](https://github.com/Niko1221/Strata/issues/5892), updated Nov15 00:55Z. RX6800 16GB +62GB RAM, QFN IQ3XXS 262K configured, real agent 32K-137K prompts, 5 prompt-read no-progress #29 and 1 verification #267 self-kills since engine0.1.59, plus unclassified SIGPIPE. HSA_ENABLE_SDMA=0 did not fix. Some restart/refill huge prompts. User RX6800 only 16GB host; much less capable. Report mostly abliterated pack but previous official GSQ also had #29, so do not attribute solely to abliterated pack.

## Peer-to-peer prompt helper (NEW)
[Strata #5999](https://github.com/Niko1221/Strata/issues/5999), updated Nov15 03:25Z; [draft PR #6001](https://github.com/Niko1221/Strata/pull/6001). 2xRTX2080Ti22GB NVLink, 32GB RAM, QFN Swift IQ3S. Opt-in P2P prefill helper: 1.6K 416→627, 3K653→830, 5.8K825→943 tok/s; multi-chunk 21.6K 1244→1325 with first/last helper. Not cross-vendor CUDA→Metal KV handoff, not directly applicable to dual M1.

## Agent workflows and numerical correctness
[Basalt #365](https://github.com/jesdga95/basalt/issues/365), updated Nov15 00:50Z: RTX5090 Laptop24 64GB GSQ IQ3XXS, f05158db short 1532-token appended tool-result prefill ~1.02-1.04 vs revert ~0.91-0.92s at8K, 1.19-1.23 vs1.06-1.08 at150K, decode unchanged; numerical consistency reason for original commit. Avoid interpreting cold prefill alone as agent latency.
[Strata #5991](https://github.com/Niko1221/Strata/issues/5991), updated Nov15 02:25Z: shipped DeepSeek Harness alpha.3 lacks model-switch pressure check added alpha.4; relevant to HaikuSwarm Molt design but not Copilot's own runtime.
[Strata #5996](https://github.com/Niko1221/Strata/issues/5996), updated Nov15 02:25Z: three local subagents on single 16GB GPU with default parallel1 ran 163/266/351 min; token usage totals >3m per helper from repeated context. Evidence for concurrency scheduling and Molt, not proof that those are unique tokens.

## Other
[Splash #770](https://github.com/incoai/splash/issues/770) asks q4_0/q5_0 KV formats; request, not implemented.
[Kapitsa #547](https://github.com/nace-ai/kapitsa/issues/547) requests KV quant; no verified new implementation.
No new verified Paperniuk DS4 DFlash2 vs MTP 128K GSQ IQ3XXS M1Max64 result from issue scan.

## Frozen controls
Two M1Max64 32GPU; RTX5070Ti16+64GB; RX6800 16+16GB host. Original GSQ IQ3XXS minimum IQ3S preferred. QFN 128K/262K. Quality, output parity and tool correctness over speed. Frozen PC first experiment original GSQ IQ3S true32K int8KV 1 slot spec1 no draft. Relay CUDA→Metal KV + recurrent-state handoff not proven. No inference code, tests, CI or model downloads authorized.

NEXT CUTOFF 2026-11-15T03:29:48Z.
