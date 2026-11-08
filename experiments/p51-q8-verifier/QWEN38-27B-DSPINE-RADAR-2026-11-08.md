# Project 51 — Tencent DSpine for dense Qwen3.8-27B secondary worker — model radar

**Research snapshot 2026-11-08T13:52:40Z**, [strict watch](./RESEARCH-WATCH-2026-11-08-0852.md). **REDISCOVERED official model published Nov7 BEFORE previous 02:32Z cutoff**. [HF model+card](https://huggingface.co/tencent/Qwen3.8-27B-DSpine-b16), [HF commit history](https://huggingface.co/tencent/Qwen3.8-27B-DSpine-b16/commits/main) first and weights files Nov7 14:20/14:33 (HF rendered clock), card updates 15:07 and15:40. [Tencent official DSpine GitHub README](https://github.com/Tencent/DSpine) still lists Qwen3.8-27B Coming soon, but actual 4.05GB safetensors model is verifiably on HF; GitHub stale, not absent weights.

A five-layer, ~2B parameter BF16 speculative DRAFT for **DENSE Qwen3.8-27B**, block16 and8192 sliding window, target verifies drafts. Separate QFN MoE model is **NOT compatible** without retraining/architecture changes; do not call a QFN speedup. Tencent's SGLang0.5.22/FA3 BF16 GPU 8-concurrent setup with reasoning xhigh and20 agent trace conversations/subset, real tool-decision **REPLAY**, not live audited code tests:
| xHigh replay lane | DFlash2 draft length | DSpine draft length | DFlash2 total TG | DSpine total TG |
| WorkBuddy Code |4.06|4.92|550.40|613.55|
| SWE-bench Pro |4.00|4.77|711.60|791.30|

Relative throughput +11.5% Code and+11.2% SWE Pro on their setup, but different DFlash2 8-block vs DSpine16-block and dynamic-verification strategy could contribute. Not guaranteed same target-specific acceptance/quality on Apple M1. Prefill/draft overhead memory from ~4GB BF16 and context8192, native Metal port NONE verified. xHigh target output correctness not increased by a sound speculative decoder (should be same distribution); proposed benefit latency only. Good secondary dense27B speed engineering lead AFTER native M1 support and direct same-target testing, not replacement of source GSQ XXS floor or source QFN DFlash2. No downloads/build executed.
