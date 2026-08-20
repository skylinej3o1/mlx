# DS4 issue #607 — two-M1-Max distributed field report

Source: https://github.com/antirez/ds4/issues/607

Related PR: https://github.com/antirez/ds4/pull/835

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

## Related PR #835 — speculative decoding over the two-node pipeline split

PR #835 adds target-verified MTP/DSpark speculation specifically to DS4's two-node **pipeline split**. The worker owns the final layers/output head/capture layers and proposes drafts; the coordinator sends multi-token verify spans through the normal two-stage pipeline.

Important protocol ideas worth mining:

- worker-side drafting so the node already owning the output/capture layers proposes the block
- **prefix commit**: partial accepts commit the already-verified prefix without replaying it token by token
- **fused spans**: on a full accept, continuation drafts are returned with the verify response so the next block can chain without an extra base-decode round trip
- whole-block verify spans for a five-draft DSpark block
- small-batch Q8_0 matmul specialized for 2–8 verification rows
- confidence/scheduler backoff so low-acceptance prose falls back toward the ordinary per-token path

### What the measurements say about PP vs our TP path

On the PR author's 2× Strix Halo Thunderbolt setup:

- plain pipeline code decode: about **13.0 tok/s**
- pipeline + DSpark: about **13.4 tok/s** on code
- prose: roughly **11.6–12 tok/s**, essentially parity with plain pipeline

The PR therefore does **not** show speculation rescuing pipeline parallelism. It mostly removes avoidable protocol overhead around speculative verification.

Our existing two-M1-Max TP result of roughly **17.5 tok/s** remains the stronger topology result. Compared with the PR's best ~13.4 tok/s PP number, 17.5 tok/s is roughly **31% faster**; versus the ~13.0 tok/s plain PP baseline it is roughly **35% faster**. These are not controlled cross-hardware benchmarks, but the direction is strong enough that MXFORGE should keep TP as the primary two-Mac DS4 path unless a same-hardware PP test proves otherwise.

### Crucial negative result inside PR #835

The PR author explicitly reports testing **tensor-parallel DSpark speculation** and choosing not to pursue it on that hardware. Their measured economics were approximately:

- plain TP: ~68 ms/token
- 6-row TP verification span: ~210–250 ms because per-layer gate exchanges remain on the critical path

That makes speculative TP net-negative unless enough drafts are accepted to amortize the multi-row communication cost. This is highly relevant to us: if we add speculative verification to our faster TP implementation, we must optimize **communication per verification span**, not simply graft the PP speculation machinery onto TP.

### MXFORGE interpretation

PR #835 is **useful as an idea mine, not as a reason to switch from TP to PP**.

For the current two-M1-Max branch:

1. Keep our ~17.5 tok/s TP path as the topology baseline.
2. Borrow prefix-commit and fused-span concepts where they can reduce TP synchronization/replay.
3. Profile TP verification at M=2..8 and measure network/collective time separately from local compute.
4. Only enable distributed speculation when expected accepted tokens exceed the measured verification break-even point.
5. Explore whether one verification collective can cover a whole block rather than paying per-layer/per-row exchanges.
6. Preserve a no-speculation fallback; on low-acceptance prose it may be the optimal mode.

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
11. For distributed speculation, report verify-span latency at M=2..8, accepted tokens per span, wire/collective time, and the break-even acceptance threshold.
12. Certify code/copy-heavy and prose/reasoning traffic separately because speculation economics differ materially.

## Research questions for our two-M1-Max setup

- What is the real Metal working-set ceiling and safe prefill headroom on each of our M1 Max 64GB machines?
- Does the contiguous F16->F16 copy path or an equivalent transient-buffer pattern exist in our chosen DS4/DSpark stack?
- How does our existing ~17.5 tok/s TP implementation compare with DS4 layer-split on the same quant, prompts, context, and Thunderbolt/network path?
- Can we keep the better decode kernels while using a lower-memory prefill path only above a context threshold?
- Should distributed runtime policy switch kernels by **available memory/context band**, just as MXFORGE switches decode/MTP policies by workload shape?
- Can prefix commits / fused verify spans reduce our TP synchronization enough to make speculation profitable?
- What is the measured TP verify break-even draft length on M1 Max at short, medium, and long context?

## Priority

High for the DeepSeek V4 branch. It does not change the immediate Qwen3.8 single-Mac tuning order, but it should be read before the next serious two-M1-Max DS4 tuning/certification round.