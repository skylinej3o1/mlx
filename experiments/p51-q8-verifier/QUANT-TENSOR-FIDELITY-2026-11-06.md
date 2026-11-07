# Source QFN tensor-level quant fidelity — new Nov 6 research gate

## November 6 2026 23:34 EST — SAME-SIZE UD v3.1 versus pristine GSQ BF16 proximity data

[Strict watch](./RESEARCH-WATCH-2026-11-06-2334.md) · [Basalt first-PC provenance and quality gate](./BASALT-UNSLOTH-V31-SOURCE-GATE.md) cutoff 2026-11-07T04:34:41Z. Source [maintainer #240](https://github.com/jesdga95/basalt/issues/240) newly scores 100×512 WikiText2 teacher-forced BF16 KL; **Wikitext2 scoring is not the imatrix/calibration dataset**. At **same total distribution size**, UD-IQ2_XS74.4GiB KL0.183/top1 86.21% versus original GSQ IQ3_XXS74.4GiB KL0.240/top1 84.03%; UD-IQ3_XXS81.6GiB KL0.119/top1 88.67% versus GSQ IQ3_S81.6GiB KL0.150/top1 87.56%. This is **vendor/source alignment proxy**, not finished-task superiority, and changes actual accepted quant/runtime source if promoted. Before user model switch require exact input `token_embd.weight` and IQ4NL PLE comparisons to understand where improvement comes from, BF16 heldout long coding, tool correctness and Apple7 resident cost. Original GSQ first PC pack dropped from Basalt publisher; source GGUF still separate. [native Basalt Q5_0 fix](https://github.com/jesdga95/basalt/commit/201e37e1a329d36bcfcaa6148a7adc6c2bb5bdd2) removes one-layer Unsloth tail blocker with no requant; no fresh post-fix TG speed claimed. Low-bit BF16 input embedding idea from [Strata #5433](https://github.com/Niko1221/Strata/pull/5433) is distinct, **unproven** for original pristine GSQ M1 memory.

Snapshot 2026-11-06T22:39:45Z. [Strict watch](./RESEARCH-WATCH-2026-11-06-1739.md). **Proposal / research only. Does not authorize creating quant packs or running owner hardware.**

## Two apparently independent precision/performance bottlenecks

### FRESH [Strata PR #5433](https://github.com/Niko1221/Strata/pull/5433) — sub8-bit input embedding matters, different machine/model

Original QFN **Unsloth UD-IQ4_XS v3.1**, **NOT original ISTA GSQ source**, `token_embd.weight` in shipped GGUF `IQ4_XS` ~322.07MiB / 4.25bpw, vs original Qwen BF16 ~1212.50MiB. On Radeon R9700 32GB/128GB host, one-component BF16 replacement:
- Relative L2 input embedding row error for compressed =8.074% mean; token embedding cosine ~0.9967 (high cosine alone hides logit effects).
- 4,995 teacher-forced positions: **244/4995=4.88% changed top1 IDs**, mean KL**0.02602** (p99 .258), docs subset91.19% agreement /88 flips and agent subset93.29% /67 flips. **Do not interpret flips as correctness gains**; compare against source BF16 full-model logits and finished tasks.
- Prose PPL4.2413→4.2090, multilingual2.6562→2.6464, docs9.5298→9.5213, overall3.9539→3.9531. 0B additional GPU VRAM on *this developer's pinned-mapped-host stream*, extra~890.4MiB pinned RAM, 4 A/B sampled decode broadly unchanged; **not automatically zero-M1 unified allocation or no context impact**.
- Sidecar auto-discovery of a preexisting `token-embd-bf16.gguf` only when main native input embedding <8bit, with type/shape validation; CUDA/HIP/Mac path claims must be validated separately. Does not fetch from service at runtime; manual pack download under HIGH only.
- Prior assumption every Unsloth input embedding Q8 false; not an assertion about **original GSQ** tensor. Need original format map and direct identical-task comparison.

### FRESH [Basalt #267](https://github.com/jesdga95/basalt/issues/267) — one unrecognized Q5_0 tensor can disable whole-model fast path

Other RTX5060Ti16/46GiB host; revised Unsloth QFN UD-IQ2_XS `blk.4.ffn_down_exps` Q5_0 breaks device-planned tail on all48 layers,4–8% experts cross PCIe. Unmodified ~65TG, single-tensor changed Q5_0→IQ4_NL ~84TG, original source GSQ IQ3XXS ~94TG. Small WikiText2 100×512 PPL modified UD**3.293** vs original GSQ**3.472** (unmodified UD PPL UNMEASURED). This is backend format admission and codebook issue, not proof quant math better; changing source one tensor changes model identity. Preferred production-quality engineering fix is type-specific optimized backend or per-layer fallback, not untracked ad-hoc requant. See [#264](https://github.com/jesdga95/basalt/issues/264) for separate Q5_K all48-fusion disabled mechanism.

### Fresh [Basalt #266](https://github.com/jesdga95/basalt/pull/266) — power/format apples-to-apples

One RTX5090 source original GSQ IQ3S 575W new **486.7TG**, previous431.1TG 489W (old mislabeled575W), 64KPP9661 vs prior9181; NVFP4-DQ8 373.7TG, Q4XL254.9TG. These rows are different quant+power settings; **match source hashes, firmware power cap, zero SSD spill and draft/head/PLE** before any speed causal claims. No M1/5070Ti extrapolation.

## Proposed acceptance criteria — NO owner execution

1. Quant inventory: hash model and revisions, PLE and input table, every `token_embd.weight` type, gate/up/down formats for48 layers, MTP and BF16 sidecar; state full package vs resident transformer and original codebook.
2. Verify BF16-vs-quant per tensor and output logits, teacher forced KLD/top1, sample size/repro/calibration imatrix provenance. All changes must preserve the source model type, no “source GSQ” label after requant.
3. Actual xHigh 128K and262K prompt occupancy, completed full tasks with tool arguments, tool execution and final artifact; numerical PPL only proxy, not acceptance.
4. For M1Max: explicit RAM/macOS/wired/swap and mapped PLE footprint, source GSQXXS minimum accepted, compare new mixed-precision candidate **only after quality superiority independently observed**. For PC first: original pristine GSQ IQ3S pack remains frozen and all hardware execution HIGH-gated.
5. Performance split cold prefill/warm suffix/cache hit/actual long decode, same sampling and draft acceptance, same hardware power and no swaps. Independent repeats and negative controls.

**Conclusion:** Neither Unsloth's claimed +15% median coding benchmark nor 4.88% embedding top1 flips are independent user M1 hard-agent proof. Research lead, not switch.
