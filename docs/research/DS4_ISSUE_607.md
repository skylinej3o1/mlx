# DS4 issue #607 — two-M1-Max distributed field report

Source: https://github.com/antirez/ds4/issues/607

Status: **CORE / promoted**

Why this matters: this is unusually close to the MXFORGE distributed target hardware: **2× MacBook Pro M1 Max 64 GB**, linked by Thunderbolt 4, running DeepSeek V4 Flash in distributed layer-split mode at 65,536 context. Treat the performance numbers as external field measurements until reproduced on our machines, but treat the failure modes as concrete certification targets.

## Reported configuration

- 2× M1 Max 64 GB, macOS Tahoe 26
- Thunderbolt 4 link
- coordinator layers `0:23`, worker layers `24:output`
- DS4 Flash `q2-q4-imatrix`, last 6 layers Q4K
- fully resident; no SSD streaming
- `--ctx 65536`
- `--dist-activation-bits 32`
- disk KV cache enabled
- reported Metal working-set ceiling ~51.3 GiB per machine
- resident model + KV + buffers ~47.05 GiB, leaving only ~4.3 GiB for prefill working memory

## Reported performance after upgrade + workarounds

Relative to commit `80ebbc3`, with the same prompts and Thunderbolt link:

- summarization prefill on 15.6K–27.4K prompts: roughly **147–163 tok/s**, with mixed small changes after upgrade
- summarization decode: roughly **9.6–9.7 -> 10.0 tok/s**, about **+4%**
- coding decode: roughly **10.8–12.6 -> 11.0–13.0 tok/s**, about **+1–4%**

Do not compare these layer-split DS4 numbers directly with our existing DSpark/TP result; the topology and runtime are different. Use them as proof that 2×64GB M1 Max is a viable DS4 field configuration and as a source of implementation/memory lessons.

## Failure 1 — coordinator without output head

A coordinator that owns only early layers stopped mapping the output tensor, leaving `weights->output == NULL`, while a startup sizing path still dereferenced it. The issue reports that restoring the previous fallback guard fixes startup:

```c
const uint64_t vocab_dim = weights->output ? weights->output->dim[1] : DS4_N_VOCAB;
```

The same coordinator-path bug was independently confirmed in the issue comments on both Metal and CUDA/DGX Spark, so distributed role-specific model ownership needs explicit test coverage.

### MXFORGE lesson

Distributed certification must test nodes that **do not own embeddings/output heads**. Never assume single-process tensor ownership in shared allocation/sizing code.

## Failure 2 — long-prefill Metal OOM from contiguous F16->F16 copy path

The report bisected a long-prefill failure to commit `427e281`. Static planned residency was unchanged; the failure appeared during command-buffer execution, consistent with transient prefill working memory rather than startup allocation.

Reported observations:

- prompts above roughly 1.4K–3K could fail on the 64GB configuration
- long prompts that worked on the older build could return Metal `Insufficient Memory`
- part of the failure range could return HTTP 200 with an empty completion, which is particularly dangerous
- lowering `--prefill-chunk` did not fix the problem
- allocation tracing did not show a normal allocator event during the failing window
- disabling only `DS4_METAL_DISABLE_CONTIG_F16_F16_COPY=1` restored long-prefill operation
- keeping the F32->F16 path enabled preserved most of the performance benefit

The author reports a 17.5K-token prompt returning to roughly **152 tok/s prefill** with that one workaround while retaining the rest of the newer kernel improvements.

### MXFORGE lesson

**Peak transient working memory is a performance feature.** Kernel optimization can increase speed while silently reducing the usable context envelope. Our certification therefore needs to record not only steady-state RSS/residency but also maximum prompt length that survives each kernel configuration.

## New DS4 certification requirements

For every two-node DS4 candidate/champion:

1. Test both coordinator and worker role-specific tensor ownership, including a coordinator that does not own the output head.
2. Test cold prefill at multiple long prompts, not only short decode benchmarks.
3. Record steady-state residency **and transient prefill headroom**.
4. Sweep at least 4K / 16K / 32K / 64K-class prompt lengths where the model/context permits.
5. Treat HTTP 200 + empty completion as a hard failure, not success.
6. Preserve command-buffer/GPU error logs alongside benchmark telemetry.
7. If a kernel win raises transient memory, record the added GiB explicitly.
8. Test both nodes simultaneously under the long-prefill load; a distributed worker can fail while the coordinator remains alive.
9. Keep toggles for suspect kernels so a speed win can be disabled selectively rather than reverting an entire optimization series.
10. Compare topology separately: DS4 layer split / RPC versus our existing DSpark tensor-parallel path.

## Research questions for our two-M1-Max setup

- What is the real Metal working-set ceiling and safe prefill headroom on each of our M1 Max 64GB machines?
- Does the contiguous F16->F16 copy path or an equivalent transient-buffer pattern exist in our chosen DS4/DSpark stack?
- How does our existing ~17.5 tok/s TP implementation compare with DS4 layer-split on the same quant, prompts, context, and Thunderbolt/network path?
- Can we keep the better decode kernels while using a lower-memory prefill path only above a context threshold?
- Should distributed runtime policy switch kernels by **available memory/context band**, just as MXFORGE switches decode/MTP policies by workload shape?

## Priority

High for the DeepSeek V4 branch. It does not change the immediate Qwen3.8 single-Mac tuning order, but it should be read before the next serious two-M1-Max DS4 tuning/certification round.