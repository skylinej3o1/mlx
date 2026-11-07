# QFN original GSQ and Unsloth 3.1 — sharing the identical 28.8GB standalone PLE shard

**Snapshot** 2026-11-07T12:18:52Z. [Strict watch](./RESEARCH-WATCH-2026-11-07-0718.md). **Research only**; no actual local downloads/links/hardlinks, GGUF conversion, .basalt pack or testing authorized.

## Artifact-level finding (new PR, other hardware)

[Strata draft PR #5479](https://github.com/Niko1221/Strata/pull/5479), created **2026-11-07T11:47:06Z**, reports `per_layer_token_embd.weight` original **IQ4_NL 28.8GB payload is byte-identical** across the original [ISTA source GGUF](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF) and [Unsloth v3.1 GGUF](https://huggingface.co/unsloth/Qwen3.8-Flash-Next-GGUF). Author specifically SHA-confirmed source ISTA 2-shard **shard2 payload** and Unsloth 4-shard **shard4 payload** `5de8b5dbf89409acc39468decafd4a4a95b13c29d88a14b0356107897829ec36`. Metadata `split.count`, `split.no`, `split.tensors.count` differs, so whole GGUF files need not have same SHA. Exact matching of all listed shard alternatives is **author-wide claim**, strongest author verified sample one source-vs-UD4 pair, don't assert individual exhaustive hash checks.

Package layouts:
- ISTA original `Q2_0, IQ2_XS, IQ3_XXS, IQ3_S`: **2 shards**, PLE shard **#2**.
- Unsloth `UD-IQ1_M, UD-Q2_0, UD-IQ2_XS`: **3 shards**, PLE shard **#3**.
- Unsloth `UD-Q2_K_XL, UD-IQ3_XXS, UD-Q3_K_XL, UD-IQ4_XS-v31`: **4 shards**, PLE shard **#4**.

Strata current native reader and `iq_pack.py` require coherent split header IDs. **Draft** PR#5479 exempts ONLY a GGUF shard whose tensor inventory is exactly one `per_layer_token_embd.weight`, preserving full validation for attention/expert/SSM and main shards. Maintainer reports `iq_pack.py --compat-bf16` with hardlink to reused ISTA PLE shard succeeded and one working live Strata0.2.11 generated tokens. **Multi-GPU physical split not run.** No proof other engines' loader accepts the same hardlink across split layouts.

## Why it matters for owner

1. **Disk/download**, not hidden RAM: share/hardlink the same ~28.8GB table between multiple original GSQ and Unsloth variants if loader supports metadata exception. One copy avoids ~28.8GB of duplicate bytes per additional quant; file hardlinks require same filesystem and proper loader semantics, otherwise may need copies. One copy does not reduce intrinsic per-token KV or M1's safe memory footprint, nor fix IQ3S 128/262K active transformer residency.
2. **Quality A/B control**: keeping source PLE bits fixed isolates variation to transformer quant/tensor mix, embeddings, MTP, sampler, draft, runner; accurate provenance and complete BF16 oracle still required. Previous same-size Basalt WikiText2 BF16 KL Unsloth UD-IQ2XS0.183 vs GSQXXS0.240 and UD-IQ3XXS0.119 vs GSQS0.150 are **proxies, not xHigh coding benchmark wins**.
3. **No silent model swaps**: frozen PC first-pass remains pristine original ISTA GSQ IQ3S in previously official Basalt v2, now absent publisher distribution; common PLE may help future permitted re-conversion but is **not** permission to create it or to substitute Unsloth.
4. **Mac implications limited**: Splash1.6 M1, Kapitsa's specialized QFN importer and other Metal runtimes are not proven to implement draft Strata's relaxed metadata check; no physical exact owner2021 M1Max32GPU source GSQ IQ3S 262K acceptance.

## Proposed HIGH-gated future QA (not executed)

Inventory GGUF shard tensor names & per-shard SHA, hash actual PLE tensor payload, validate mismatched header exception only for single-tensor shard, detect wrong architecture/dims/quant and conflicting first-shard metadata, test source GSQ original IQ3XXS/3S logits+multi-turn with reused PLE, confirm SSD bytes/swap and cache behavior, test 2-Mac split separately. Do not copy/hardlink or alter packaged models automatically.

