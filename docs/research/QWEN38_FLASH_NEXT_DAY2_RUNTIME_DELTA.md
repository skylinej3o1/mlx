# Qwen3.8-Flash-Next day-two runtime delta

Status: **FRESH FIELD EVIDENCE / high relevance to 2x M1 Max MXFORGE target**

Updated: 2026-08-27 afternoon.

## Executive delta

Several important results appeared after the first day-one scans:

1. A dedicated Apple `mlx-serve` implementation with the 51.2B PLE removed from resident MLX weights now reports roughly **60 tok/s serial decode, 78 tok/s on code with native MTP, and ~730 tok/s prefill** on an M4 Max 128GB. The model uses 4-bit routed experts, 8-bit sensitive non-expert paths, BF16 controls, and a 4-bit SSD/mmapped PLE sidecar. Resident memory is ~75GB. This is the closest public architecture match yet to the planned MXFORGE hierarchy.
2. The same implementation reports that MTP is highly workload-dependent: about **+41% on code**, but slightly slower on prose and on one 8.5K prompt. Therefore native MTP should be adaptive, not blindly always-on.
3. A separate M5 Max 128GB llama.cpp user rearranged the Unsloth GGUF so PLE tensors can remain mmap/SSD-backed instead of Metal-wired. Wired memory fell from ~123GB to ~97GB while decode remained **36 tok/s without MTP**. This is direct Apple evidence that moving the PLE to SSD can be effectively throughput-neutral in a real full-model run.
4. PipeNetwork published a strong quant-sensitivity study. Uniform 4-bit is badly degraded on WikiText-2 (ppl 5.3914 vs 4.4708 BF16), while 4-bit routed experts + 8-bit sensitive non-expert weights gives ppl 4.5286, only +1.3%. Uniform 6-bit and 8-bit are statistically indistinguishable from BF16 on that corpus. The ~4B non-expert/control weights are roughly 20x more quantization-sensitive per parameter than the 121B routed-expert pool.
5. The Baekpica/ds4 SSD-PLE project has now crossed from isolated correctness into integrated serving. Its Q5 variant (77.55 GiB resident compute + BF16 PLE sidecar) runs full 48-layer prefill/decode on a DGX Spark with a 262K-configured server; at 5.38K prompts it measures 154.6 tok/s prefill / 34.9s TTFT / 18.7 tok/s decode, and at 21.0K prompts 149.1 tok/s prefill / 141.3s TTFT / 18.8 tok/s decode. Increasing the bounded PLE cache from 512 MiB to 2 GiB produced only ~0.6% prefill improvement on the tested workload.
6. No credible direct M1 Max Flash-Next benchmark has surfaced yet. The key remaining uncertainty for the user's 2x64GB M1 Max setup is distributed execution efficiency, not model viability or SSD-PLE feasibility.

## Apple runtime result closest to MXFORGE

Source: `ddalcu/Qwen3.8-Flash-Next-MLX-Serve-mixed-4-8bit`.

Reported M4 Max 128GB configuration:

- routed experts: 4-bit group 64;
- attention / GDN / hyper-connections / indexer / shared experts: 8-bit group 64;
- lm_head: 8-bit;
- embed_tokens: 4-bit;
- routers, inject gates, norms, convs, SSM state: BF16;
- native MTP head uses the same mixed policy as the trunk;
- 51.2B PLE: one **32.0GB 4-bit `ngram_table.bin`**, mmap-backed rather than loaded into MLX weights;
- per token, CPU dequantizes only the 16 selected rows and transfers the resulting 2560-vector;
- total resident footprint: roughly 75GB plus KV/state.

Current measured claims on M4 Max 128GB, mlx-serve 26.8.11:

- serial decode: ~60 tok/s;
- code with MTP: ~78 tok/s, about +41%;
- prose with MTP: about 4% slower than serial;
- one 8.5K-prompt MTP case: about 4% slower;
- prefill: ~730 tok/s;
- sparse-attention needle at ~24.8K recovered;
- prefix cache enabled.

This result replaced an earlier first-port figure of ~29-34 tok/s decode / ~400 tok/s prefill, demonstrating how immature and tunable the runtime still is.

### Relevance to 2x M1 Max

Official Apple bandwidth:

- M1 Max 32-core GPU: 400 GB/s;
- top M4 Max 40-core GPU: 546 GB/s.

A single M4 Max at 60 tok/s does **not** imply 2x M1 Max will exceed 60 tok/s. The M1 pair cannot be treated as one 800 GB/s memory pool because inter-node communication and PP/TP bubbles matter. However, the result substantially raises the plausible ceiling and suggests the previous ~40 tok/s two-node target is no longer aggressive if the distributed path is efficient.

For pure sequential PP, a crude bandwidth anchor from 60 tok/s on 546 GB/s gives ~44 tok/s at 400 GB/s before M1-vs-M4 compute/kernel differences and inter-node transfer. A higher-precision Q5-class trunk lowers that somewhat; a successful code-oriented MTP path can restore or exceed it. Treat this only as an anchor, not a benchmark projection.

## Direct Apple SSD-PLE evidence

A separate M5 Max 128GB user modified the Unsloth UD-Q4_K_XL GGUF layout so PLE tensors are no longer interleaved with Metal-wired tensors. With default mmap behavior:

- wired memory before layout fix: ~123GB including OS;
- after fix: ~97GB;
- roughly 26GB of wired footprint removed;
- decode stayed ~36 tok/s without MTP.

This is direct evidence that the Apple SSD/mmap PLE tier can be effectively throughput-neutral for decode when the tensor layout permits the OS to page the table independently.

It also confirms the packaging rule already identified by MXFORGE: PLE should be a first-class sidecar / independently pageable region, not mixed into accelerator-resident shards.

## Quant sensitivity: important correction to generic Q4/Q5 thinking

PipeNetwork tested BF16, 8-bit, 6-bit, uniform 4-bit, and a mixed 4/8-bit MLX build over 296,815 WikiText-2 tokens / 145 windows.

| Build | PPL | Delta vs BF16 |
|---|---:|---:|
| BF16 | 4.4708 | baseline |
| 8-bit | 4.4749 | statistically indistinguishable |
| 6-bit | 4.4767 | statistically indistinguishable |
| mixed 4/8 | 4.5286 | +1.3% |
| uniform 4-bit | 5.3914 | +20.6% |

The mixed 4/8 recipe uses:

- 121B routed experts at 4-bit;
- sensitive non-expert weights (attention, DeltaNet, hyper-connections, shared experts, embeddings, lm_head) at 8-bit;
- tiny router/control set at BF16;
- PLE at 4-bit group 32.

Ablations show that no single sensitive group explains the loss; hyper-connection gates and attention/DeltaNet paths each account for a large fraction. The conclusion for MXFORGE is strong:

> Do not define the production quant by one global bit-width. Spend precision on the ~4B sensitive always-active/control path and compress the 121B routed expert reservoir more aggressively.

This weakens the case for a naive all-Q5 build and strengthens a **Q5-class heterogeneous recipe** such as Q5 experts + Q8 control/non-expert/MTP, or even Q4 experts + Q8 control as a speed baseline.

## Baekpica Q5 SSD-PLE integrated serving

The dedicated ds4 implementation now has a Q5 variant with:

- resident compute payload: 77.5456 GiB;
- BF16 PLE sidecar: 95.3682 GiB;
- Q4_K / Q5_K / Q5_0 routed expert tiers;
- bounded PLE cache and O_DIRECT sidecars;
- full 48-layer prefill/decode serving on one DGX Spark.

Measured under a 262,144-token configured server and no prefix-cache reuse:

| Prompt | Prefill | TTFT | Decode |
|---|---:|---:|---:|
| ~5.38K | 154.6 tok/s | 34.91 s | 18.7 tok/s |
| 21,037 | 149.1 tok/s | 141.28 s | 18.8 tok/s |

A 512 MiB vs 2 GiB PLE cache A/B at 21K changed prefill only ~0.6%, suggesting very large explicit PLE caches may not be necessary for at least this workload.

Caveats: MTP, full 262K prompt characterization, full-model quant quality, multi-sequence batching and SSD latency percentiles remain pending.

## Updated MXFORGE implications

### Quant target

Current preferred production direction:

```text
routed expert bulk        Q5 first serious quality target
                          Q4 as speed baseline
attention/GDN/QSA/HC      Q8 or protected mixed precision
shared experts            Q8-ish
lm_head                   Q8
routers/control/norms     BF16 where cheap
MTP                       Q8-ish / separately tuned
PLE cold                  Q8 production target initially
PLE reference             BF16 SSD for exactness certification
PLE hot                   dequantized FP16/BF16 or OS page cache
```

PipeNetwork's data shows that protecting the non-expert path matters more than globally raising all expert bits.

### Performance forecast

Do not promote a measured M1 number yet: none exists.

But the M4 Max mlx-serve result materially raises the plausible ceiling. A reasonable current framing for a **mature Q5-class 2x M1 Max 64GB system at ~30K coding context** is:

- conservative successful distributed port: ~30-38 tok/s;
- expected tuned range: ~38-50 tok/s;
- current midpoint: ~43-45 tok/s;
- strong result: 50+ tok/s;
- stretch: 55+ tok/s.

The dominant uncertainty is two-node execution efficiency. PP will preserve capacity with relatively low communication but cannot sum both nodes' bandwidth for one token; TP can expose more aggregate bandwidth but may lose badly to Thunderbolt/network synchronization. MTP and the M>1 verifier geometry may create hybrid opportunities.

For prefill, the M4 result (~730 tok/s) is particularly encouraging. Even after large M1-generation and distributed penalties, a two-node target in the several-hundred-tok/s range now looks plausible if QSA/GDN kernels are well tuned.

## Evidence status

- M4 Max ~60 tok/s serial / ~78 tok/s code MTP / ~730 tok/s prefill: **community measured, single implementation, needs independent reproduction**;
- M5 Max SSD-PLE mmap with ~26GB wired-memory reduction and unchanged ~36 tok/s decode: **community measured**;
- mixed 4/8 quant perplexity study: **published paired corpus measurement, stronger than anecdotal quality claims**;
- DGX Spark Q5 SSD-PLE integrated serving: **measured by artifact author, full 48-layer serving up to 21K prompt tested**;
- direct M1 Max Flash-Next result: **still absent**;
- 2x M1 Max Flash-Next performance: **forecast only**.

## Sources

- https://huggingface.co/ddalcu/Qwen3.8-Flash-Next-MLX-Serve-mixed-4-8bit
- https://huggingface.co/pipenetwork/Qwen3.8-Flash-Next-MLX-mixed-4_8bit
- https://www.reddit.com/r/LocalLLM/comments/1vz927j/got_qwen38nextflash_ngram_ssd_offload_working_in/
- https://huggingface.co/Baekpica/Qwen3.8-Flash-Next-Mixed-Quant-SSD-PLE-GGUF/commit/f77e47a8db4781db7d51e7d0e9a29ecf595a57e2
- https://support.apple.com/en-us/111901
- https://support.apple.com/en-us/121553
