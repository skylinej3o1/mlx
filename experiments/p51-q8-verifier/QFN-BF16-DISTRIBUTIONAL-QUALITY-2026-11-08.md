# Nov 8 2026 — independent BF16-reference QFN quality at 399600 positions

[Watch](./RESEARCH-WATCH-2026-11-08-1635.md), cutoff 2026-11-08T21:35:14Z. FRESH [Strata #5610](https://github.com/Niko1221/Strata/issues/5610) created20:12Z, other RTXPRO6000 Blackwell96GB +253GB host Windows, Strata0.2.12/engine0.1.58 vs customized llama.cpp BF16 truth and exactly same GGUF per quant. Teacher forcing 400 segmentsx1000,399600 scored positions, top64 normalized KL(REF||RUN), top1, no speculation/adaptive routes/live agent tools. MIT/public-domain software and novels.
| Quant version | llama.cpp top1/KL | Strata top1/KL |
|---|---|---|
|UD-Q4_K_XL pre-Nov4 V3.1|94.02%/.0526|94.39%/.0461|
|UD-IQ4_XS Nov4 Dynamic3.1|92.29%/.0852|92.53%/.0808|
|original ISTA GSQIQ3_S|89.80%/.1577|89.81%/.1580|
Strata same-quant GSQIQ3S essentially parity, Unsloth rows slightly closer to BF16. Limit: BF16 reference is llama.cpp only, raw4GB bundle attached but not independently rerun, top64 not full dist, Q4XL older revision, no native Apple7/8 or xHigh finished coding. No source GSQXXS Strata-vs-llama row claimed. Tensor source matters: prior [Strata PLE override #5588](https://github.com/Niko1221/Strata/pull/5588) Unsloth external Q8 opened but embedded IQ4NL silently chosen. Exact PLE/weights/hash and matched full tools needed before quality promotion.
