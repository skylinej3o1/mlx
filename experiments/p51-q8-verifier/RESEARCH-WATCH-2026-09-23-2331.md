# Project 51 primary-lane research watch — 2026-09-23 23:31 ET

**Freshness boundary checked:** prior hard boundary **2026-09-24 02:09:05 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-24 03:31:38 UTC**. Agention AP and BottleCap ThinkingCap are included as **RECOVERED OLDER EVIDENCE** because they materially inform the quant/behavioral-efficiency thesis but were published before this delta.

## Decision

**No canonical TG/PP or xhigh-quality target change.**

No new exact 2x M1 Max 64 GB / direct-TB4 Flash-Next sustained-throughput receipt appeared, and no new DASLab / GSQ-RCO xhigh behavioral-quality result appeared.

This pass is nevertheless meaningfully mechanism-positive because a fresh Apple/Flash-Next PR directly optimizes the MTP verify path rather than target-only decode:

- MTP verify forward at S=3/5/7 improves roughly **9–13%**;
- sampled/greedy MTP decode on an M5 Ultra improves roughly **12–21%** in the reported cells;
- the optimization is simply routing verify rows through an already-existing fused MoE rows kernel instead of the sorted gather/QMV chain.

That is exactly the class of verifier-cost reduction P51 needs, but it remains M5-Ultra transfer evidence and does not establish the exact M1/TB4 ~1.5-target-forward verifier regime.

## Findings

### NEW — mlx-serve #519: fused MoE verify rows improve exact Flash-Next MTP decode materially on M5 Ultra

Source: https://github.com/ddalcu/mlx-serve/pull/519  
Created: **2026-09-24 03:24:53 UTC**.

A single-slot Flash-Next MTP verify with B=1 and 2<=S<=8 was sending routed experts through the sorted chain: block sort, gathers and three stock affine_gather_qmv launches per layer. The existing fused MoE rows arm already supports arbitrary row counts and is bit-identical per row to S=1 decode, so verify rows are now routed through it.

M5 Ultra 256 GB, macOS 27.0, Qwen3.8-Flash-Next mixed 4/8-bit, bf16 KV:

| cell | fused rows | old sorted chain | change |
|---|---:|---:|---:|
| verify S=3 forward | 17.29 ms | 19.78 ms | **-12.6%** |
| verify S=5 forward | 20.73 ms | 23.41 ms | **-11.4%** |
| verify S=7 forward | 25.77 ms | 28.37 ms | **-9.2%** |
| llmprobe MTP decode, typical=0.2 | 147.8 / 147.9 TG | 129.2 / 135.2 TG | **~+12%** |
| 512-token greedy MTP decode | 190.8 TG | 164.8 TG | **+16%** (n=1) |
| sampled MTP decode (0.6/0.95/20) | 213.6 TG | 177.2 TG | **+21%** (n=1) |

The llmprobe rows arm showed **lower tokens/step** (2.70/2.67 vs 3.15/3.56), but the verify step itself fell to ~18 ms from ~24-26 ms, so end-to-end decode still increased. The author has not yet isolated whether acceptance changed due sampling variance or the depth controller adapting to the cheaper verify path.

Correctness checks:
- GSM8K 59/60 vs 59/60;
- MMLU-Pro 54/70 vs 54/70;
- six-task coding set 6/6 vs 5/6;
- 2,639 tests passed.

Greedy text differs between verify arms, so this is not a bit-identical end-to-end speculative path comparison; the other verify kernels were already not bit-identical to S=1.

**Classification:** NEW exact-model-family Apple transfer evidence.

**P51 consequence:** this is the strongest fresh evidence in this pass for the central verifier thesis. It demonstrates that a large piece of verify overhead can come from a poor small-row MoE dispatch choice, and that reusing a fused rows path can remove roughly a tenth of whole verify-forward time on Apple hardware. It strongly supports:
- dedicated verify-width dispatch policies;
- avoiding sorted/gather chains for tiny verification matrices;
- measuring verifier forward directly at S=3/5/7 rather than extrapolating from S=1 decode.

**Target impact:** no numeric change. M5 Ultra is not Apple7/M1, acceptance moved between arms, and this does not by itself establish ~1.5 target-forward equivalents. It modestly reduces mechanism risk without changing the formal ~70% >=40-TG planning confidence.

### UPDATE — mlx-serve #517 confirms target-only GDN fusion does not materially move MTP cells

Source: https://github.com/ddalcu/mlx-serve/pull/517  
Fresh comment: **2026-09-24 03:31:16 UTC**.

The preceding target-only GDN fusion (#517) was remeasured with MTP:
- MTP decode: **136.5 / 134.0 TG** vs **132.7 / 131.5 TG** with the fusion disabled, about +2% and within run spread;
- 2K prefill: unchanged at roughly **2400 tok/s**.

The author explicitly attributes the MTP-side improvement instead to #519, because #517 only changes S=1 while MTP verify executes at S>=2.

**P51 consequence:** reinforces the need to keep **target-only decode optimization and verifier optimization as separate ledgers**. A good S=1 kernel improvement should not automatically be credited to speculative throughput.

### UPDATE / WATCH — vLLM #58454 connects speculative kpool corruption to observed long-reasoning degeneration

Source: https://github.com/vllm-project/vllm/pull/58454  
Fresh discussion: 2026-09-24 02:39–03:24 UTC.

The underlying fix predates this boundary. Fresh discussion links it to the open GLM-5.3-Flash long-decode degeneration reports on 8xB200 / NVFP4 / FP8 KV.

Mechanism:
- with speculative width >=2, rejected drafts can overwrite committed keys in a per-request tail ring before acceptance is known;
- when a pool-completing draft is rejected, later drafts may already have overwritten slots belonging to committed positions;
- at the next recompression the pool summary key can be wrong;
- the bug only matters after context exceeds index_topk=2048, where pools compete for sparse selection.

The standalone repro shows **106/128 FP8 key bytes differ** under the old ring sizing and exact equality under the enlarged ring. The issue reporter and PR author agree the mechanism plausibly matches the production degeneration signature, but an end-to-end patched production A/B had **not yet been run by the cutoff**.

**Classification:** UPDATE / plausible root-cause connection, not yet confirmed.

**P51 consequence:** long-xhigh speculative validation must include rollback/rejection across sparse-indexer pool boundaries, not merely short acceptance tests. Temporary proposal storage must be sized/owned such that rejected rows cannot alias committed sparse-indexer state. Final text correctness at short context is insufficient.

### RECOVERED OLDER EVIDENCE — vLLM #58489 operationalizes the PLE-lifetime rule without an extra copy kernel

Source: https://github.com/vllm-project/vllm/pull/58489  
Created before this boundary; fresh activity in-window was review/CI.

The prior state already recorded #58441's finding that side-stream PLE lookup can read overwritten graph-pool IDs. #58489 is the concrete fix:

- compute n-gram/prefetch IDs directly into a persistent per-layer output buffer;
- no new kernel and no extra copy;
- memory cost is max_num_batched_tokens * ngram_heads * 8 bytes per PLE layer;
- 51 tests pass;
- the reproduction sees overwritten -1 values 3/3 on main and reference IDs after the fix.

**P51 consequence:** prefer **produce-directly-into-stable-storage** over enqueue-then-copy when side-stream lifetime is known at graph construction time. This is a cleaner implementation template for PLE/QSA sidecars.

### RECOVERED OLDER EVIDENCE — SGLang #40041: exact Qwen3.8-Next PLE verify fusion is a ~2% end-to-end decode win

Source: https://github.com/sgl-project/sglang/pull/40041

The PR fuses Qwen PLE gate/normalization/convolution preparation specifically for target verification. Reported result:
- **~2% end-to-end decode improvement**;
- AIME26 **95%**;
- acceptance length unchanged.

No substantive benchmark change occurred in this window; the PR was simply updated/rebased. It was missing from the durable P51 state and is therefore recovered rather than called new.

**P51 consequence:** another exact-family example that verify-specific fusion contributes a few percent at system level. Together with mlx-serve #519, it supports the expectation that the 2.3x -> ~1.5x verifier program is a stack of multiple targeted reductions rather than one single breakthrough.

### UPDATE / merged correctness evidence — SGLang #40754: fused shared-expert loader can silently zero the shared expert

Source: https://github.com/sgl-project/sglang/pull/40754  
Merged commit: e2f4fedf04fe at **2026-09-24 03:21:33 UTC**.

On a Qwen3.8 FP8 MoE path, text-only weight loading failed to remap shared-expert weights into the fused expert slot. The server still loaded and served, but every shared expert was effectively zeroed and GSM8K collapsed near random.

After fixing the loader:
- 1,104 missing shared-expert warnings -> 0;
- known-good GSM8K: **97.49%**;
- fixed build: **97.41%**.

**P51 consequence:** protected shared-expert precision is not enough; **loader/packing integrity is part of quant certification**. Production validation should assert expected tensor/expert counts and run a behavioral smoke test after any prepacked/fused quant conversion. A model that loads and emits tokens is not evidence that all protected islands were actually loaded.

### RECOVERED OLDER EVIDENCE — Agention Precision Qwen3.8-27B quants strengthen the "bit allocation matters more than nominal Q-level" thesis

Public sources:
- Agention Qwen3.8-27B-AP-GGUF model card;
- LocalLLaMA release thread.

This is dense Qwen3.8-27B, **not Flash-Next**, and it is behavioral-fidelity evidence only indirectly.

Agention evaluates each quant against the same BF16 next-token distribution using upstream llama.cpp KL-divergence tooling, 60x2048-token chunks over three corpora. Same-size comparisons use the same GGUF tensor type/file size; the difference is calibration/encoding.

Selected same-size results:
- IQ4_XS held-out KLD: **0.0276 Unsloth -> 0.0255 AP** (-7.6%);
- Q3_K_XL: **0.0421 -> 0.0380** (-9.9%);
- IQ3_S: **0.0617 -> 0.0568** (-7.9%) on held-out and **0.0404 -> 0.0384** on web, though Unsloth remains better on wikitext-2 (**0.0470 vs 0.0528**);
- AP IQ3_S worst-1% held-out KLD **0.491 vs 0.553** for Unsloth;
- held-out BF16 top-1 match at AP IQ3_S: **87.6%**.

Against ISTA GSQ-RCO at approximately the same low-bit size:
- AP IQ3_S 11.21 GiB: held-out **0.0568**, web **0.0384**, wikitext **0.0528**;
- GSQ-RCO IQ3_S 11.29 GiB: **0.0594 / 0.0432 / 0.0665**.

The model card itself correctly limits the claim: KL fidelity is not a downstream-task leaderboard and downstream evals are still needed.

**P51 consequence:** this strengthens the structural case for aggressive heterogeneous/per-tensor optimization in the 3.x region. It does **not** prove source-like xhigh behavior at 3.3-3.6 BPW, and it does not invalidate the behavioral-certification hierarchy. Treat KLD/worst-tail divergence as an optimizer/early-screening objective, not the final shipping gate.

### RECOVERED OLDER EVIDENCE — ThinkingCap shows behavioral token compression can preserve native MTP efficiency

Source: BottleCap ThinkingCap-Qwen3.8-27B model card/blog.

ThinkingCap is a fine-tuned **dense 27B** checkpoint, not a quant and not Flash-Next.

At xhigh across twelve benchmarks:
- macro accuracy: **86.6% base -> 85.8% ThinkingCap**;
- mean thinking-token reduction: **37.2%**;
- LiveCodeBench: **91.14 -> 91.21** with -20.3% thinking;
- Terminal-Bench 2.1: **75.84 -> 75.28** with -10.7%;
- AIME26 is the major cost: **98.13 -> 94.27** with -30.2%.

Critically, native MTP remained effectively intact:
- base drafted-token acceptance: **54%**, ~2.6 tokens/step;
- ThinkingCap: **53%**, ~2.6 tokens/step.

The evaluation used H200, vLLM 0.29.0, MTP k=3 and xhigh on both sides.

**P51 consequence:** "behavioral compression" (fewer xhigh reasoning tokens) and runtime speculative acceleration can coexist rather than trading directly against each other. This is potentially a separate future product branch for effective wall-clock speed, but **not** part of the canonical P51 source-model target because P51's current goal is to reproduce the original model's behavior, not fine-tune it to think less.

## Checked surfaces / negative results

- **antirez/ds4:** no issue, PR or commit activity in-window.
- **IST-DASLab/GSQ:** no issue, PR or commit activity in-window.
- **llama.cpp:** no fresh P51-relevant Metal/Flash-Next performance change in-window.
- **oMLX:** no new exact Flash-Next/M1 throughput receipt. Cluster work was active but did not provide a new relevant performance receipt by the cutoff.
- **mlx-serve:** #519 is the major fresh result; #517 follow-up clarifies target-only vs verify-specific gains.
- **vLLM:** #58454 is a fresh root-cause linkage; #58489 is a recovered concrete implementation of an already-known lifetime rule. Other in-window activity was screened as generic frontend/CI/platform work.
- **SGLang:** #40754 merged correctness fix is material; #40041 is recovered exact-family verify-fusion evidence. XPU Flash-Next enablement merged, but its own PR explicitly says performance tuning has not started, so it receives no performance credit.
- **Community/Hugging Face:** Agention AP and ThinkingCap are recovered prior evidence, not post-02:09 discoveries. No precisely timestamped new post-boundary source-vs-quant xhigh behavioral certification or exact M1/TB4 Flash receipt was found.

## Canonical planning state after this pass

Unchanged:

- Flash-Next xhigh production quant search: **~3.0-3.6 average BPW**.
- likely source-like xhigh region: **~3.3-3.6** (engineering hypothesis only).
- dual-M1 Flash: **40 TG @ ~128K**, **400 cold PP**.
- planning confidence for >=40 TG: **~70%**.
- first-principles central TG region: **~39-41**.
- practical mature-system downside TG: **~30-32**, conditional on at least modest speculation benefit.
- physical target-only fallback: **~24-27**.
- cold-PP derived center: **~370-390**, downside **~320-340**.
- single-M1 27B: **25 TG**.
- RTX 5070 Ti 27B: **120 TG** mature target.

## New hard boundary

**2026-09-24 03:31:38 UTC**
