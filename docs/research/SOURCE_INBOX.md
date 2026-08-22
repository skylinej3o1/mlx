# MXFORGE unresolved source inbox

Purpose: preserve user-supplied research links immediately when the source cannot yet be inspected reliably. Resolve each item into `docs/MXFORGE_SOURCE_CATALOG.md` once the source content/configuration can be verified; do not infer claims from an opaque share URL.

## 2026-08-21

- https://www.reddit.com/r/oMLX/s/JR5dbVaMfI
  - Status: **RESOLVED WITH HIGH CONFIDENCE / canonical target inferred from subreddit feed**
  - Likely canonical post: https://www.reddit.com/r/oMLX/comments/1vumbhw/experience_with_ane_on_m1_max_64gb/
  - Title: `Experience with ANE on M1 Max 64GB`
  - Area: Qwen3.8-27B heterogeneous ANE/GPU prefill on exact M1 Max 64GB hardware class.
  - Evidence: subreddit enumeration found a same-hour fresh post matching the share link context; the opaque `/s/` token itself still did not resolve directly, so retain the original shortlink alongside the inferred canonical URL.
  - Configuration: `Qwen3.8-27B-oQ4e-fp16-mtp`, Engine Auto, Code (Python); custom-kernel HEAD build; GS64; Prompt Block 1024; `Use both ANE` disabled on single-die M1 Max.
  - Reported results: ANE improved TTFT by 32.1% at pp1025 and 18.4% at pp4097; prompt-processing TPS rose 134.5->198.0 (+47.2%) and 139.7->171.1 (+22.5%). Peak memory rose by ~9.54-9.64 GB. tg was essentially flat at pp1025 (18.4->18.3) and measured higher at pp4097 (15.0->17.5), but treat decode movement as workload/run-sensitive rather than an ANE decode claim.
  - MXFORGE action: promote this from indirect M1/M1 Pro evidence to **direct M1 Max 64GB evidence** for the heterogeneous-prefill branch. Reproduce on our exact Qwen3.8 quant/champion and sweep GS64, prompt block, ANE/GPU fraction, memory overhead, and context-dependent ANE enable/disable thresholds.
