# M1 Max quant refresh — Qwen3.8-27B and Ornith-1.5-35B-A3B

Status: **CORE / current Apple deployment evidence**

Updated: 2026-08-22

This note refreshes the practical M1 Max 32-core GPU / 64 GB picture for Qwen3.8-27B and adds direct same-hardware evidence for Ornith-1.5-35B-A3B. External oMLX results are community benchmarks, not MXFORGE-certified measurements. Keep runtime, context, quant, speculation, KV precision, prompt type and memory settings attached to every number.

## Executive conclusion

The current M1 Max picture splits cleanly:

- **Qwen3.8-27B** remains the stronger general-capability target, but public long-context throughput depends heavily on MTP, verifier implementation, SpecPrefill, KV policy and prompt-processing strategy.
- **Ornith-1.5-35B-A3B** is a raw-throughput monster on M1 Max because only ~3B parameters are active per token. Clean oQ4e autoregressive decode already reaches roughly 62 tok/s at 4K, 56 tok/s at 32K and 44 tok/s at 64K without MTP, TurboQuant or ANE.
- For Ornith, start simple. Do not assume speculation improves throughput. Validate ordinary AR first, with unquantized KV for tool-use quality, then add MTP/KV compression only under paired workload tests.

## Qwen3.8-27B — architecture

Official model:

- https://huggingface.co/Qwen/Qwen3.8-27B

Relevant structure:

- dense 27B hybrid model
- 64 layers
- 48 Gated DeltaNet / linear-recurrent layers
- 16 full-attention layers
- hidden size 5120
- native MTP
- native context 262,144

Because the target is dense, decode remains strongly weight-bandwidth-sensitive. Unlike Ornith, every generated token pays for essentially the full 27B body.

## Qwen3.8-27B — clean oQ4e baseline on M1 Max

Public oMLX M1 Max 32c / 64 GB evidence for `Qwen3.8-27B-oQ4e-fp16-mtp` with MTP disabled shows approximately:

| Context | PP tok/s | TG tok/s | Peak MLX memory |
|---:|---:|---:|---:|
| 1K | 152.0 | 19.1 | 16.4 GB |
| 4K | 148.5 | 18.5 | 17.7 GB |
| 8K | 148.5 | 18.1 | 18.1 GB |
| 16K | 141.8 | 17.2 | 19.0 GB |
| 32K | 136.6 | 15.2 | 20.8 GB |
| 64K | 117.2 | 11.3 | 23.3 GB |
| 128K | 91.7 | 6.0 | 27.6 GB |

Interpretation: plain Q4 is usable but its long-context TG erosion is significant. The large gap between these results and the tuned stack below shows that runtime architecture matters at least as much as the raw quant label.

## Qwen3.8-27B — strongest public practical M1 stack found

Model:

- https://huggingface.co/chimpanzeetaxidriver/Qwen3.8-27B-oQ4e-G128-fp16-mtp

Representative oMLX benchmark:

- https://omlx.ai/benchmarks/performance/cdgvivho

M1 Max 32c / 64 GB, oMLX 0.6.2, Code (Python), `oQ4e-G128-fp16-mtp`, Lightning MTP + SpecPrefill + TurboQuant KV4:

| Context | PP tok/s | TG tok/s | Peak MLX active |
|---:|---:|---:|---:|
| 16K | ~650.4 | ~25.5 | ~19.6 GB |
| 32K | 633.9 | 23.4 | 20.0 GB |
| 64K | 568.8 | 20.9 | 20.8 GB |

32K settings include:

- TurboQuant KV 4-bit
- SpecPrefill enabled
- draft model `Qwen3.5-0.8B-MLX-oQ4-fp16`
- SpecPrefill keep_pct 0.2
- Lightning MTP enabled
- ANE prefill disabled in this particular run

This is not a pure quant benchmark. It is evidence for a **complete practical stack**. The dramatic PP numbers are mainly a prompt-processing/system result, not an oQ4-vs-Q8 property.

### Practical Qwen quant ranking

#### Performance / long-context daily use

`oQ4e-G128-fp16-mtp` is currently the strongest public M1 Max performance lead found. Its ~23.4 tok/s at 32K and ~20.9 tok/s at 64K are the most relevant public agent-context numbers in this refresh.

Caveat: Q4 target weights + 4-bit KV should be evaluated on the user's actual coding/tool workload before treating it as a quality-default configuration.

#### Quality-first / verifier research

Q8 FP16 remains the important quality and execution-regularity branch. Public M1 numbers are not spectacular in stock configurations, but MXFORGE's own real-ruler work proves that verifier routing and Metal kernel geometry materially move Q8 throughput.

Current MXFORGE frozen ruler:

- model: `Qwen3.8-27B-oQ8e-fp16-mtp`
- M1 Max 32c / 64 GB
- 29,297-token real coding prompt
- 512 generated tokens
- temperature 0, seed 1, thinking disabled

Current project evidence from `experiments/p51-q8-verifier/STATUS.md`:

- target-only baseline: 10.536 tok/s
- stock Lightning MTP: ~15.59 tok/s
- P54F certified D3/M4 verifier mean: **18.504 tok/s** at 29,297 real context
- P58 FP16 fused-GDN route: **+2.37% paired TG**, -2.460 ms/backbone-cycle, bit-exact for the directly compared q/k/v/conv-state tensors
- P59 reproduced the fusion at +2.00% same-session, but absolute system drift prevented promotion of a new global absolute champion

Do not compare these real-29.3K Q8 values directly to older short-context ~27-29 tok/s Q6-ish tuner runs.

#### Q5/Q6 middle ground

MLX/oMLX conversion families place Qwen3.8-27B roughly around:

- oQ4e: ~17 GB class
- oQ5e: ~20 GB class
- oQ6e: ~23.7 GB, ~6.7 bpw class
- oQ8e: materially larger, ~high-20 GB class before cache/runtime overhead

There is not yet a clean current M1 Max Q5/Q6 benchmark set comparable to the tuned G128-Q4 stack or the project Q8 29.3K ruler. Q6 remains attractive as a quality/speed compromise, but should be certified locally rather than inferred from old short-context results or newer-chip reports.

#### Extreme fit / utility worker

A recent mixed 3-bit MLX build is ~12.7-13.0 GB and reports reasonable single-stream speed, but this is a capacity/utility option rather than the preferred quality branch. Use only after coding/tool regressions are measured.

## M1/M2 tensor precision rule

For these Apple generations, prefer **FP16 for the non-quantized tensors** unless a specific route has been certified otherwise. Several M1/M2-oriented oMLX/MTPLX builds explicitly provide FP16 variants, and the MXFORGE P58 work found a useful FP16-specific verifier path.

## ANE prompt processing is independent of decode quant

Direct M1 Max field evidence for `Qwen3.8-27B-oQ4e-fp16-mtp` showed roughly:

- ~1K PP 134.5 -> 198.0 tok/s with ANE
- ~1K TTFT 7.62 -> 5.18 s
- ~4K PP 139.7 -> 171.1 tok/s
- decode near 1K essentially unchanged, 18.4 -> 18.3 tok/s
- peak-memory penalty ~9.5-9.6 GB

Therefore ANE should remain a **cold-prefill/TTFT lever**, enabled only when its memory cost is justified by context and expected future session work. See `QWEN38_M1_ANE_PREFILL.md`.

# Ornith-1.5-35B-A3B

Official model:

- https://huggingface.co/ornith-ai/Ornith-1.5-35B-A3B

Architecture:

- 35.9B total parameters
- ~3B active per token
- 256 experts
- 8 routed + 1 shared expert active pattern
- 40 layers
- 30 linear-attention + 10 full-attention layers
- native vision
- 262,144 native context
- MIT license
- thinking enabled by default

The architecture explains its extreme M1 speed: unlike dense Qwen3.8-27B, decode only reads/executes a small active expert subset per token plus always-active shared/attention components.

## Direct M1 Max oQ4e autoregressive results

Representative benchmark:

- https://omlx.ai/benchmarks/performance/9pgjog3d

`Ornith-1.5-35B-A3B-oQ4e-fp16`, M1 Max 32c / 64 GB, oMLX 0.6.2, Code (Python), with **MTP off, TurboQuant off, SpecPrefill off and ANE off**:

| Context | PP tok/s | TG tok/s | Peak MLX active |
|---:|---:|---:|---:|
| 4K | 1,037 | 61.9 | 20.8 GB |
| 8K | 926.2 | 60.1 | 21.0 GB |
| 16K | 836.7 | 58.6 | 21.3 GB |
| 32K | 723.6 | 56.2 | 22.0 GB |
| 64K | 530.0 | 44.4 | 23.5 GB |

This is the most important finding in the refresh.

The model does not need speculative decoding to be fast on M1 Max. At 32K it is already ~56 tok/s, with ~724 tok/s prompt processing, using only ~22 GB MLX active memory.

## Ornith MTP results

Other M1 Max 64 GB oMLX runs with bundled MTP show roughly:

- oQ4e + MTP: ~58.0 tok/s at 4K and ~59.4 at 16K in one set
- oQ4e + MTP + TurboQuant KV4: ~53.1 at 1K and ~47.6 at 4K in another set

These do **not** establish that MTP is a win. The clean AR oQ4e benchmark is already 61.9 at 4K and 58.6 at 16K. Workload, runtime settings and speculative acceptance need paired tests.

MXFORGE action: Ornith should start with a simple AR control. Add MTP only after measuring accepted tokens per verification and effective wall-clock throughput on a replayed coding workload.

## Ornith higher-bit M1 results

### oQ6e FP16

A direct M1 Max 64 GB oMLX run reports approximately:

- 4K PP ~949.5 tok/s
- 4K TG ~51.5 tok/s
- ~28.5 GB MLX active peak

This run had MTP disabled despite the model name carrying an MTP suffix.

Q6 therefore gives substantial quality headroom while preserving excellent interactive speed, at roughly a ~17% 4K TG penalty versus the clean oQ4e AR result.

### oQ8e FP16 + MTP

Direct M1 Max 64 GB oMLX results report approximately:

- 1K: ~55.4 tok/s, ~38.1 GB peak
- 4K: ~53.3 tok/s, ~39.0 GB peak

Q8 remains remarkably fast for a 35.9B-total model because only ~3B parameters are active per token. The price is memory, not catastrophic decode throughput.

No equally clean 32K/64K M1 Q8 series was found in this pass. Do not extrapolate 4K TG flatly to long context.

## Ornith quality-oriented quant candidates

### 6-bit XL MLX

- https://huggingface.co/leonsarmiento/Ornith-1.5-35B-A3B-6bit-XL-mlx

This community build uses architecture-role precision rather than one uniform bit-width:

- router/shared gates, lm_head and shared expert: BF16
- embeddings, self-attention and linear-attention: 8-bit
- vision tower and routed experts: 6-bit
- ~6.8 bpw, ~28 GB class
- MTP omitted

This is a particularly interesting quality-first M1 Max candidate because Ornith's sparse experts dominate storage while always-active routing/attention/output components retain higher precision. It needs direct paired M1 quality/performance certification before promotion over oQ6e/oQ8e.

### Dynamic GGUF fidelity evidence

Atomic Dynamic quantization reports the following 35B-A3B reference points against its BF16 conversion:

| Quant | Size | Mean KLD | Top-1 match |
|---|---:|---:|---:|
| Q6_K | 28.51 GB | 0.0167 | 94.63% |
| AD-Q6_K-Q5_K | 26.25 GB | 0.0158 | 94.85% |
| Q5_K_M | 24.73 GB | 0.0269 | 93.31% |
| AD-Q5_K-Q4_K | 22.14 GB | 0.0251 | 93.52% |
| Q4_K_M | 21.17 GB | 0.0477 | 91.01% |
| AD-Q4_K-IQ4_XS | 20.13 GB | 0.0315 | 92.71% |

Source thread:

- https://www.reddit.com/r/LocalLLaMA/comments/1vsx94f/we_quantized_the_new_ornith_15_9b_and_35ba3b/

These are GGUF/KLD fidelity measurements, not MLX M1 throughput results. The transferable lesson is that **non-uniform quant allocation can materially improve fidelity at the same or smaller footprint**, which supports an eventual M1-specific Ornith quant/layout search.

## Ornith capability / quality caveat

Ornith AI reports very strong agentic-coding and tool-use scores, including gains over Qwen3.6-35B-A3B on SWE-bench and Terminal-Bench. Treat these as vendor-reported until independently reproduced on the intended harness.

Community experience is mixed. One recent first-impression thread reports tool-call problems when KV quantization was enabled, improving after KV quantization was removed:

- https://www.reddit.com/r/Qwen_AI/comments/1vtlvys/ornith_15_35b_first_impression/

This is anecdotal, but it is operationally important enough to influence the first experiment.

**First Ornith quality test should use unquantized/default KV.** Only reintroduce TurboQuant / lower-bit KV after paired tool-call and coding-agent evaluation.

## Recommended M1 Max 64 GB deployment ladder

### Qwen3.8-27B

1. **Fast practical long-context:** `oQ4e-G128-fp16-mtp` + Lightning MTP + SpecPrefill; compare TQ4 versus higher-quality KV on actual agent traces.
2. **Quality/research:** `oQ8e-fp16-mtp` with the MXFORGE D3/M4 verifier stack; continue P60 long-KV attention and later reduced-vocab/custom-MTP work.
3. **Middle-quality candidate:** oQ5e/oQ6e FP16, but run a fresh matched 4K/16K/30K/64K certification before choosing it over Q4/Q8.
4. **Memory-first worker:** mixed 3-bit only for utility/swarm use after quality evaluation.

### Ornith-1.5-35B-A3B

1. **Speed-first:** oQ4e-fp16, plain AR. This is already ~56 tok/s at 32K and ~44 tok/s at 64K.
2. **Likely quality/speed sweet spot:** oQ6e-fp16 or a carefully designed ~6.8-bpw mixed-precision MLX quant.
3. **Quality-first on 64 GB:** oQ8e-fp16 if ~39 GB model/runtime footprint leaves enough room for the desired context and application memory.
4. Start with ordinary KV and no speculation; add MTP/TurboQuant only when paired agent tests prove a net win.

## Practical role split

At current evidence levels:

- **Ornith Q4/Q6:** fast local coding worker, interactive agent, parallel/swarm node. Extremely attractive on M1 Max.
- **Qwen3.8-27B Q4 tuned:** faster general Qwen deployment with strong long-context practicality.
- **Qwen3.8-27B Q8 MXFORGE:** quality-first and systems-research target; slower today but offers a clean substrate for verifier/kernel work.

Do not infer that Ornith is globally smarter because it is faster. Its ~3B-active MoE architecture trades active compute for sparse capacity, while Qwen3.8-27B spends essentially the full dense body every token. Capability must be decided by real held-out coding/tool/reasoning tasks, not tok/s.

## Immediate experiments worth running

1. Ornith oQ4e AR at 4K / 16K / 29-32K / 64K on the exact M1 Max 64 GB machine.
2. Repeat oQ4e with MTP, keeping prompt/sampling/KV identical; log acceptance and effective TG.
3. Ornith oQ6e or 6-bit XL at 4K / 16K / 30K with unquantized KV.
4. Run the same coding/tool-use replay suite on Ornith Q4/Q6 and Qwen3.8 Q4/Q8.
5. Only after correctness/behavior is stable, sweep KV4/KV6/KV8 and MTP together.

Primary metric remains **successful useful work per wall-clock second at the target context**, not raw short-context tok/s.