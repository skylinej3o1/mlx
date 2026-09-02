# Runtime Research Watch — 2026-09-01 Night

Scope: deeper external pass on Qwen3.8-Flash-Next, Qwen3.8-27B, and
DeepSeek-V4-Flash/DS4 with emphasis on the exact dual-M1-Max/TB4 topology.
This is a delta from `RESEARCH-WATCH-2026-09-01-POST-EARLY-EVENING.md`.
It does **not** modify the certified P69 verifier state. **P69B13 remains
next, using existing profiling data only.**

## DeepSeek V4 Flash / DS4 — the missing dual-M1 TG anchor exists

Source: https://github.com/antirez/ds4/issues/607

A July field report predating the 0731 checkpoint measured the exact hardware
class and network topology we care about:

- 2x MacBook Pro M1 Max 64 GB;
- direct Thunderbolt 4 cable;
- coordinator layers 0:23 / worker layers 24:output;
- `q2-q4-imatrix`, final six layers Q4_K;
- fully resident on both machines, no SSD streaming;
- 65,536 context;
- 32-bit distributed activations.

Measured decode after the then-current DS4 update/workarounds:

- long-document summarization: **10.03 / 10.07 tok/s**;
- code generation, 401-2,977-token prompts: **11.00-12.95 tok/s**.

Measured long-prompt prefill:

- 17.5K: **155.3 tok/s**;
- 27.4K: **162.7 tok/s**;
- 15.6K: **153.7 tok/s**.

The prior build was only slightly slower:

- summarization decode: 9.60 / 9.67 tok/s;
- code decode: 10.83-12.63 tok/s;
- long-prompt prefill: 147.1-163.0 tok/s.

### Important qualification

This is **not 0731**. Issue #607 was created July 26, before the July-31
checkpoint, and used an older q2-q4-imatrix model/layout plus 32-bit
inter-machine activations. Therefore these TG numbers must not be presented as
DeepSeek-V4-Flash-0731 performance.

However, it is the strongest direct calibration yet for the *hardware and
execution topology* itself. It establishes that a straightforward serial
layer split across two M1 Maxes is a low-teens decode system, not a near-2x
single-node decode multiplier.

This makes the topology economics clearer:

- the previously found 0731 Quality128 run at ~152 tok/s distributed prefill
  is fully consistent with the older field report;
- high dual-M1 decode numbers cannot come from layer splitting alone;
- reaching the 30s on Flash-Next requires model-specific advantages such as
  resident state, removal of SSD expert traffic, high-acceptance MTP, verify
  windows, microbatch/concurrent-agent pipeline filling, and deliberate overlap.

## DeepSeek V4 Flash 0731 — exact dual-M1 state remains TG-unreported

Source: https://github.com/antirez/ds4/issues/922

The newer exact setup remains:

- 2x M1 Max 64 GB / TB4;
- DeepSeek-V4-Flash-0731 DS4-Quality128 (95.76 GiB);
- layers 0:22 / 23:output;
- 8-bit distributed activations;
- 262K context allocation;
- 34,384-token prompt;
- ~152 tok/s distributed prefill;
- 51K CLI prompt also completed;
- after moving the model mmap from external USB SSD to internal NVMe, 34K
  prefill + generation completed successfully.

The issue still provides no generated-token count or sustained decode TG, so
the 257-second total after the storage fix cannot be converted into a valid TG
measurement.

Practical interpretation: use #607 as the topology anchor and #922 as the
0731 long-context correctness/prefill receipt. Do **not** merge their numbers
into a fake 0731 TG measurement.

## Qwen3.8-Flash-Next — exact same 2x M1 Max/TB4 hardware is now proven coherent

Source: https://github.com/ggml-org/llama.cpp/issues/27993

The author of the DS4-0731 report also tested Flash-Next on exactly:

- 2x MacBook Pro M1 Max 64 GB;
- point-to-point TB4, ~0.8 ms RTT;
- Unsloth UD-IQ4_XS, 93.7 GiB;
- llama.cpp RPC tensor/layer split.

The original >~2K-prompt all-zero failure was fixed by llama.cpp PR #27960.
After rebuilding at `cc231cb`, the reporter confirmed coherent 2.5K and 4K
needle tests and coherent q8_0 KV behavior. They then started a 115K-token
needle test at 256K context.

No PP/TG throughput was published in the issue. Therefore this remains a
correctness/topology receipt, not a speed receipt.

The useful architectural lesson is that recurrent/QSA state correctness across
RPC boundaries is nontrivial. Distributed Flash-Next bring-up needs deep-context
needle/correctness gates before any throughput number is trusted.

## Flash-Next single-M1 ceiling signals

### Tuned M1 Max 64 GB custom llama.cpp

Source: https://www.reddit.com/r/LocalLLM/comments/1w02u3f/qwen38flashnext_on_low_memory_systems/
Source: https://www.reddit.com/r/LocalLLaMA/comments/1w296bx/qwen38flashnext_optimised_for_macs/

The current custom-M1-Max work reports approximately:

- ~12 tok/s target-only;
- ~15 tok/s with MTP in an intermediate configuration;
- ~18 tok/s MTP peaks on coding;
- later tuned configurations around ~17.6-22 tok/s depending on context and
  MTP configuration;
- ~165-190 tok/s prefill after additional tuning.

These numbers are much more relevant to the two-M1 plan than M5/M3-Ultra
absolute throughput because they expose how much performance is already
available from one 400-GB/s M1 Max even while using SSD streaming.

### AtomicChat 64 GB MacBook proof-of-concept

Source: https://www.reddit.com/r/Qwen_AI/comments/1vzf3nh/running_85gb_qwen_38_quant_on_64gb_macbook/

A special 85 GB Flash-Next quant with the n-gram table isolated to its own
SSD-backed GGUF shard reports:

- **517.9 tok/s prefill**;
- **36 tok/s decode**;
- 45.8 GB resident + 39.1 GB SSD for the demo quant.

The demo quant is explicitly described by its author as imperfect
(top-1 vs BF16 82.68%, mean KLD 0.2277), and the post does not specify the
exact MacBook chip in the text. Treat 36 tok/s as a hardware-unspecified 64 GB
MacBook ceiling/proof-of-concept, not an M1-Max calibration.

The durable insight is the n-gram-storage asymmetry: SSD can hold the sparse
lookup table cheaply because only tiny indexed slices are touched per token,
whereas routed expert streaming is fundamentally much more expensive.

## Qwen3.8-27B — a new speculative acceptance signal worth preserving

Source: https://github.com/ARahim3/mlx-dspark

The current mlx-dspark project now reports DFlash 2 as its Qwen3.8-27B winner
on an M4 Pro 48 GB under current MLX.

DFlash 2 uses a candidate-path selector plus dynamic convolutions to increase
acceptance at the same verifier width rather than simply widening verification.

Current project-level measurements include:

- 8-bit Qwen3.8-27B: roughly **24-34 tok/s** depending on domain;
- 4-bit: roughly **25-38 tok/s**;
- same-session DFlash2-vs-DSpark comparison at width 8:
  - 8-bit DFlash2 mean speedup ~3.63x, acceptance ~5.53;
  - 4-bit DFlash2 mean speedup ~2.30x, acceptance ~5.14;
  - 4-bit example ~33.8 tok/s.

The project also documents a critical long-context effect: fixed wide verify
windows can become net-negative as attention-KV rereads grow with context, so
newer versions adapt verify width to context depth.

### Relevance to P51/P69

This does **not** supersede the exact-Q8 P69 ruler:

- hardware differs (M4 Pro versus M1 Max);
- target quant/runtime differs;
- DFlash2 uses a separate learned drafter;
- the P69 campaign is optimizing native target-verifier execution with frozen
  exactness requirements.

But it strongly reinforces the P63 conclusion that **acceptance per unit of
verify cost** is the right speculative objective. If the exact target-kernel
campaign eventually reaches diminishing returns, a separate DFlash2-style
acceptance experiment is higher-priority than blindly increasing native MTP
verify width.

## Qwen3.8-27B exact challenge frontier

Source: https://github.com/Layr-Labs/qwen-3.8-mtp-challenge

Fresh check still shows:

- best score `3.7291100105909`;
- #1481 newest visible submission;
- no #1482+ promoted result.

No new exact-Q8 external frontier changes P69B13 selection.

## Updated decisions

1. **We now have a real dual-M1 decode anchor:** pre-0731 DS4 on exact 2x M1
   Max 64 GB / TB4 measured ~10-13 tok/s decode and ~150-163 tok/s long-prompt
   prefill.
2. **Do not relabel that as 0731.** The 0731 Quality128 receipt remains
   ~152 tok/s prefill + successful generation, with TG unreported.
3. **Naive PP2 does not double B1 decode.** Any mature Flash-Next target in the
   30s requires model-specific MTP/verify overlap or concurrent pipeline fill,
   not merely putting half the layers on each Mac.
4. **Flash-Next distributed correctness is real but still immature.** The exact
   2x M1 llama.cpp RPC setup required #27960 before >2K prompts were coherent;
   deep-context correctness must precede benchmarking.
5. **The single-M1 software ceiling keeps moving upward.** M1-specific custom
   Flash-Next work is already in the high-teens/low-20s with MTP, which means
   the dual-node project should first reproduce the best single-node path and
   then measure what residency/overlap actually adds.
6. **DFlash2 is a meaningful future 27B architecture lead.** It improves
   acceptance at fixed width and supports the existing P63 economics thesis,
   but remains a separate post-kernel campaign.
7. **Certified exact state is unchanged.** P69B12 remains frozen and
   **P69B13 remains next using existing profiling data only.**
