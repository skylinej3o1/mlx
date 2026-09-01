# Latest external runtime watch

Read:
`experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-01-MORNING.md`

Also read the focused kernel-mining note:
`experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

The mining note records the portable large-batch quantized-weight panel-reuse pattern: store weights compactly, decode/repack a compute panel once, reuse it across enough activation/expert rows to amortize conversion, and gate the path by measured batch geometry.

The morning runtime watch adds the latest Qwen3.8-Flash-Next long-text gathered-QSA admission, adaptive-vs-fixed MTP depth evidence, expanded Fusion warm-turn/cache results, lean B1 scheduling work, and DS4 multi-request pipeline-parallel support.

This pointer tracks the newest external Qwen3.8-Flash-Next / Qwen3.8-27B / DeepSeek-V4-Flash-0731 research delta plus focused optimization mining. External evidence does not modify the certified P69 checkpoint; consult `CURRENT.md` for verifier state.
