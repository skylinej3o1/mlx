# Qwen3.8-Flash-Next day-one Apple / quant field note

Status: **FRESH FIELD EVIDENCE / use for MXFORGE planning, not yet certification-grade**

Updated: 2026-08-26 evening, several hours after public weight release.

## Executive read

The first hours after release materially strengthen the case for an MXFORGE Flash-Next port:

1. MLX / oMLX support exists already and native MTP works on Apple Silicon.
2. A community oQ4 MLX build with native MTP has demonstrated short-generation speeds in the ~29-40 tok/s band on an unspecified Apple M3 Studio; a uniform 8-bit build measured ~20.07 tok/s without MTP and ~24.90 tok/s with MTP over repeated 512-token runs, with exact greedy-output parity and ~70.8% acceptance.
3. A 6-bit MTP build on the same M3 Studio measured ~20.65 tok/s without MTP and ~25.94 tok/s with three draft tokens over repeated 512-token runs, again with exact greedy-output parity. This is important evidence that Flash-Next MTP provides a real ~24-26% sustained decode gain in an Apple runtime, not just on B200/H200.
4. No credible direct M1 Max Flash-Next benchmark has surfaced yet. The public M1 posts found so far are about Qwen3.8-27B, not Flash-Next.
5. Existing monolithic MLX Q4/oQ4 builds are roughly 104-106 GiB and therefore do not fit on one 64GB M1 Max. A community oQ6-MTP build is ~147.2 GiB. For 2x64GB M1 Max, a custom distributed layout plus PLE sidecar remains the right path.
6. The first dedicated SSD-PLE artifact has already implemented the same general memory hierarchy MXFORGE proposed: Q5/Q6 resident compute backbone, high-precision MTP/always-active paths, BF16 PLE stored as an SSD sidecar with bounded cache. Its isolated SSD-vs-resident PLE path is byte-exact; integrated full-model serving and throughput are still pending.

## Primary field sources

- Official architecture / benchmark release: https://qwen.ai/blog?id=qwen3.8-flash-next
- Official weights: https://huggingface.co/Qwen/Qwen3.8-Flash-Next
- Vontra MLX oQ4 + MTP: https://huggingface.co/Vontra/Qwen3.8-Flash-Next-MLX-oQ4-MTP
- Vontra MLX oQ6 + MTP: https://huggingface.co/Vontra/Qwen3.8-Flash-Next-MLX-oQ6-MTP
- Vontra MLX 8-bit + MTP: https://huggingface.co/Vontra/Qwen3.8-Flash-Next-MLX-8bit-MTP
- AtomicChat imatrix GGUF ladder: https://huggingface.co/AtomicChat/Qwen3.8-Flash-Next-GGUF
- Baekpica SSD-PLE Q5/Q6 artifact: https://huggingface.co/Baekpica/Qwen3.8-Flash-Next-Mixed-Quant-SSD-PLE-GGUF
- Strix Halo 128GB first llama.cpp field run: https://www.reddit.com/r/StrixHalo/comments/1vz5yb3/qwen38flashnext_125ba6b_running_on_strix_halo/
- RTX PRO 6000 NVFP4 field run: https://www.reddit.com/r/LocalLLM/comments/1vz20ap/qwen38flashnextnvfp4_on_single_rtx_pro_6000_120ts/

## Apple MLX evidence

### Uniform 8-bit + native MTP

Vontra reports oMLX 0.6.3rc3 on an Apple M3 Studio, greedy decode, three repeated 512-token runs:

- MTP off: 20.0693 tok/s median
- MTP on, 3 draft tokens: 24.8956 tok/s median
- delta: +24.05%
- drafted: 1004
- accepted: 711
- acceptance: 70.82%
- exact-output parity: passed

This is the cleanest Apple MTP measurement found so far because it uses repeated sustained runs and publishes the acceptance telemetry.

### 6-bit + native MTP

Vontra reports on the same Apple M3 Studio:

- MTP off: 20.6495 tok/s median over 3x512
- MTP on, 3 draft tokens: 25.935 tok/s median
- delta: +25.6%
- drafted: 1055
- accepted: 776
- acceptance: 73.55%
- exact-output parity: passed

A separate sensitivity-guided oQ6-MTP package reports short warmed generations ranging from ~28-37 tok/s, with ~70.8-84.2% acceptance; these are less controlled than the repeated 512-token numbers above.

### oQ4 + MTP

The sensitivity-guided Vontra oQ4-MTP package reports on an Apple M3 Studio:

- warmed 32-token raw completion: 34.4 tok/s
- casual 71-token chat: 39.7 tok/s
- acceptance range: 58.3-89.5%

These are encouraging but short and prompt-dependent. The repeated 512-token 8-bit/6-bit tests are better anchors for sustained behavior.

### Plain 4-bit, no MTP

A Vontra uniform 4-bit MLX build reports:

- warmed 543-566-token oMLX responses: 24.1-24.2 tok/s
- shorter warmed oMLX responses: 24.6-26.1 tok/s
- short standalone smoke test: 31.0 tok/s

The monolithic file is ~103.9 GiB because the PLE is also quantized and resident.

### M1 Max status

No direct Qwen3.8-Flash-Next M1 Max benchmark was found as of this note. Public M1 Max reports currently found refer to Qwen3.8-27B rather than Flash-Next. Do not silently substitute M3/M5 Studio numbers as M1 evidence.

This means the 2x M1 Max throughput forecast remains a forecast until a local MXFORGE port or credible public M1 run exists.

## First non-Apple field anchors

### Strix Halo 128GB

A user running the first llama.cpp support PR with Unsloth UD-IQ4_XS (~87 GiB) reports approximately:

- ~23 tok/s decode
- ~390 tok/s prefill
- no MTP yet

A second earlier run reported ~20 tok/s with UD-Q4_K_XL. These are community measurements, not controlled certification.

### RTX PRO 6000 96GB NVFP4

A community vLLM run reports:

- PLE offloaded to host RAM
- no MTP: ~80-90 tok/s decode, ~10k tok/s prefill
- MTP: roughly +50% decode, ~-10% prefill
- headline ~120 tok/s generation with MTP

This is useful as proof the architecture can be very fast with a tuned sparse-offload implementation, but not transferable numerically to Apple.

## Quant landscape

### AtomicChat imatrix GGUF ladder

AtomicChat currently recommends:

- Q4_K_M: default balance
- UD-Q4_K_XL: Q4-class with embeddings/output held at Q8_0
- Q6_K: near-lossless
- Q8_0: reference-quality

Their public model card claims Q4_K_M and above stay within roughly a point or two of full precision, but no large independent downstream quant-vs-BF16 eval is attached yet. Treat this as provisional.

### Inferencerlabs early quant-fidelity table

A modified-MLX quant test reports:

- Q4.5: token accuracy 91.65%
- Q5.5: 95.05%
- Q6.5: 96.65%
- Q8.5: 97.65%
- Q9: 97.80%

This is useful directional evidence that Q5.5 is materially closer to higher precision than Q4.5, but the methodology/sample is not strong enough to translate directly into SWE-bench or agent quality.

## Dedicated SSD-PLE mixed-quant artifact

Baekpica has already published a Flash-Next artifact explicitly designed around an SSD PLE sidecar. It is targeted at DGX Spark / a custom ds4 runtime, not Apple, but the layout is directly relevant to MXFORGE.

Resident compute recipe:

- routed expert gate/up, interior layers 2-45: Q5_K
- edge-layer expert gate/up: Q6_K
- expert down main path: Q6_K
- expert-down 128-column tail: Q5_0
- MTP experts and most always-active matrices: primarily Q8_0
- hyper-connection / unsupported / vision tensors: BF16
- norms, gates, recurrent/control state: F32 where required

PLE:

- 51.2B PLE kept BF16 in SSD sidecar
- sidecar: ~95.37 GiB
- bounded 512 MiB / 1 GiB / 2 GiB page-cache targets
- async prefetch and exact hashed-row lookup

Measured artifact sizes:

- resident Q5/Q6 compute backbone: ~90.96 GiB
- BF16 SSD PLE: ~95.37 GiB

Correctness work already passed in isolation:

- SSD-gathered PLE rows match resident BF16 byte-for-byte
- exact hashing checked against Transformers on 595,616 row IDs
- forced cache eviction/reload passes
- PLE forward/injection and persistent convolution-state comparisons are exact
- sidecar remains bounded rather than being mapped resident in full

Still pending:

- integrated 48-layer serving
- full-model quality
- end-to-end throughput
- SSD stall distribution
- MTP integration

This is highly relevant because it independently converges on a **Q5/Q6 backbone + high-precision MTP/control paths + SSD PLE** design.

## What this implies for the 2x M1 Max target

The first public monolithic MLX quants are not the final shape we want:

- oQ4-MTP: ~105.5 GiB total resident package
- oQ6-MTP: ~147.2 GiB total resident package
- 8-bit-MTP: ~189 GiB total resident package

They include the PLE in the MLX weight payload. Therefore a single 64GB M1 Max cannot run the useful Q4+ packages resident, and even two 64GB machines do not comfortably hold the public oQ6 package as-is.

For MXFORGE the desired package remains custom and heterogeneous:

```text
2x M1 Max 64GB

resident/distributed:
  main compute backbone at ~Q5-ish
  MTP at Q6/Q8 or mixed precision
  routers / GDN / QSA / HC / control tensors protected
  hot PLE cache

SSD-backed:
  complete PLE table, likely Q8 first production target
```

### Recommended initial quality target

The emerging public recipes make Q5 look more—not less—reasonable:

- all-Q4 is the speed/default community path;
- Q6 is the near-lossless path;
- the first SSD-aware mixed artifact chooses Q5/Q6 selectively for the compute backbone and Q8 for MTP/always-active paths;
- early quant-fidelity measurements show a meaningful Q4.5 -> Q5.5 gain.

So the current MXFORGE first serious target should remain:

> **Q5-class compute backbone, Q8 PLE on SSD, protected high-precision control/router/GDN/QSA/HC tensors, native MTP retained and separately tuned.**

The exact bit allocation should be measured rather than copied blindly from GGUF because MLX/Metal kernel economics differ.

## Forecast impact

The new Apple evidence does not justify replacing the prior 2x M1 Max ~30K Q5 forecast with a measured number, because no M1 Max Flash-Next run exists yet and the M3 Studio configuration is unspecified.

But it raises confidence in several assumptions:

- native MTP can give a real ~24-26% sustained Apple decode improvement;
- Flash-Next is already viable in MLX/oMLX;
- a custom SSD-PLE hierarchy is practical enough that an independent implementation has already passed exact isolated correctness gates;
- Q5/Q6 selective quantization is a credible architecture-aware choice rather than a purely theoretical recipe.

The remaining dominant uncertainties for 2x M1 are distributed execution efficiency and Apple SSD-PLE latency hiding, not whether the architecture can be represented or whether native MTP works on Apple at all.
