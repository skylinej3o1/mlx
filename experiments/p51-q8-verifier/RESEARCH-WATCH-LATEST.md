# Project 51 research watch — November 15, 2026, 09:23 EST

Previous cutoff 2026-11-15T11:45:32Z; new cutoff 2026-11-15T14:23:03Z. Targeted connected GitHub scan. UPDATED issue != created within window. Research-only, no code/CI/hardware/model downloads.

## Metal backend progress (NEW)
[Strata #6028](https://github.com/Niko1221/Strata/issues/6028), updated 2026-11-15T13:57:53Z: Gyro-M on Metal in 0.2.13, 128GB Apple Silicon, conversation A/B/A parking restores A in ~42ms. PR6024 no PLE table Metal wrap (37.57GB of91.97GB), PR6025 TQP5/6/7 expert parity for Gyro-L, PR6026 PLE-only GGUF loading, PR6027 serve tests all open; PR3960 tool recovery pending rebase. NOT QFN M1Max64 performance.

## Agent tool-call robustness (NEW)
[Strata #6022](https://github.com/Niko1221/Strata/issues/6022), updated 2026-11-15T13:22:59Z: QFN Unsloth UD-Q4KXL with Claude Code, Hermes, Cursor ~48 declared tools; model invents TaskCreate/Delete or alternate XML syntax; parser drops tool call and leaks raw markup into content with finish_reason stop. Proposed per-row speculative-compatible declared-tool-name mask and broader parser, not implemented confirmed. Score declared-tool accuracy, structured calls, markup leakage separately.

## JSON state isolation regression (NEW)
[oMLX #5301](https://github.com/jundot/omlx/issues/5301), updated 2026-11-15T12:54:10Z: M1Max32GB Gemma4-26B-A4B4bit MLX, oMLX0.7.3 vs0.7.0. With response_format json_object fallback to prompt injection (xgrammar absent), temperature0, R response depends on whether Q ran before it, cached_tokens0, deterministic per order. Replay 1076 classification requests yields 27/1021 binary and 3/55 choice argmax changes across versions; 0.7.4/0.8.0 not tested. Model/runtime differs from QFN DS4; suggests state-isolation gate.

## Basalt / dense 27B (UPDATED)
[Basalt #319](https://github.com/jesdga95/basalt/issues/319) asks for dense Qwen3.8-27B support as bridge to potential Qwen4-27B; request only, no support confirmed.
[Basalt #366](https://github.com/jesdga95/basalt/issues/366) 5070Ti16+64GB UD IQ3XXS 128K 0.4.0 expert budget39GiB slowdown vs38GiB workaround persists, no confirmed merged fix.
[Basalt #374](https://github.com/jesdga95/basalt/issues/374) RTX5090D24 192GB 1M YaRN needle14-16/16 and startup-dependent decode 110-143 remains report, not owner setup.
[Strata #5965](https://github.com/Niko1221/Strata/issues/5965) dual RX7900XT Linux prefill ~1100→~600 after simultaneous engine/ROCm/apt upgrade, causal attribution unresolved.

## Paperniuk and Relay
Paperniuk DS4 latest observed commit 9da1288 Nov12; Splash fork d61103e Nov12; no new same-GSQ QFN IQ3XXS M1Max64 128K DFlash2-vs-MTP measurement. Previous oMLX CUDA helper DGX Spark→M3Ultra 10GbE 64K ~2400 vs Mac~1000 tok/s remains interesting but does NOT prove RTX5070Ti16→M1Max64 full-state Relay. No verified Qwen4-27B open weights in this targeted scan.

## Owner frozen controls
2x M1Max64 32GPU, RTX5070Ti16+64GB RAM, RX6800 16+16GB host. GSQ IQ3XXS minimum, IQ3S preferred. QFN 128K/262K. Quality/parity/schema-valid tools first. Frozen first PC Basalt original GSQ IQ3S true32K INT8KV 1 slot spec1 NO DRAFT. No inference experiments or code/CI changes authorized.

NEXT CUTOFF 2026-11-15T14:23:03Z.
