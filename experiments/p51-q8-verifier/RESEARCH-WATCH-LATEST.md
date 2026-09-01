# Latest external runtime watch

Read:
`experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-01-AFTERNOON.md`

Also read the focused kernel-mining note:
`experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

The mining note records the portable large-batch quantized-weight panel-reuse pattern: store weights compactly, decode/repack a compute panel once, reuse it across enough activation/expert rows to amortize conversion, and gate the path by measured batch geometry.

The afternoon runtime watch adds oMLX exact SSD expert streaming for Flash-Next, the updated cached-drafter 100K restart receipt, and measured single-GB10 multi-agent comparison targets (~93 tok/s B4 and ~102 tok/s B8), while preserving the midday long-context/PP-vs-TP findings.

This pointer tracks the newest external Qwen3.8-Flash-Next / Qwen3.8-27B / DeepSeek-V4-Flash-0731 research delta plus focused optimization mining. External evidence does not modify the certified P69 checkpoint; consult `CURRENT.md` for verifier state.
