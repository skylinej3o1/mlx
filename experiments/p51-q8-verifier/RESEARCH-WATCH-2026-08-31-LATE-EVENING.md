# External Qwen + DS4 late-evening delta — 2026-08-31

This note is a delta against `RESEARCH-WATCH-2026-08-31.md` at branch checkpoint `042d3fadfab9e4989e8e839ca68e75ade5ea513b`.

These are external upstream/community results, not measurements produced by this repository. Keep measured facts separate from deployment inference.

## Executive delta

- Qwen3.8-27B Layr-Labs MTP frontier remains `3.7291100105909`; no new promotion changes P69B13.
- Flash-Next has a new multi-sequence correctness warning: llama.cpp `qwen4exp` recurrent split replay remains corrupt when recurrent-state rollback is force-enabled, even though the single-sequence restore test passes.
- A previously promising dual-GB10 Flash-Next TP2/NEXTN profile has been explicitly withdrawn after real multi-turn re-prefill traffic produced an independent invalid-probability/device-assert failure despite passing bounded long-generation and retrieval qualification.
- llama.cpp merged a Metal radix `TOP_K` path with large long-row/multi-row kernel microbenchmark wins. This is promising for QSA/indexer work on Apple, but there is no end-to-end Flash-Next receipt yet.
- No new DS4 Flash-0731 distributed throughput result changes the topology conclusion from the prior watch.

## Flash-Next: multi-sequence recurrent rollback is not yet trustworthy

llama.cpp issue #28019 isolates a `qwen4exp` state-replay problem that matters specifically for multi-request serving.

The architecture is currently excluded from `llm_arch_supports_rs_rollback()`. When the reporter force-enables recurrent-state rollback:

- a single-sequence recurrent checkpoint/restore test passes;
- the multi-sequence split-replay test fails badly;
- reported maximum logit difference is `9.25491`, first observed for sequence 0 at position 16.

The suspected uncovered state includes Qwen4-Exp-specific recurrent/auxiliary state such as PLE convolution history and possibly QSA indexer state. That diagnosis is not yet a merged fix.

The same report gives a useful concurrency symptom on GB10 / Flash-Next IQ4_XS with three parallel sequences: rewrite-oriented ngram speculation was about 50 aggregate tok/s while speculation-off was about 66–70 aggregate tok/s. That is not an Apple number, but it shows why a B1-valid rollback mechanism must not be assumed to scale automatically to several agent streams.

Source: https://github.com/ggml-org/llama.cpp/issues/28019

### Decision impact

For the dual-M1 agent server, separate these gates:

1. B1 target-only correctness;
2. B1 native-MTP rollback correctness;
3. 2–5 concurrent target-only streams;
4. 2–5 concurrent context/ngram drafting;
5. native multi-stream MTP only after a split-replay test proves every recurrent/PLE/QSA state component is sequence-isolated and exactly restorable.

Do not treat single-sequence recurrent rollback as sufficient evidence for the 3–5-agent configuration.

## Flash-Next: dual-GB10 TP2 profile withdrawn after real agent traffic

The public `hellojiaru/qwen38-flash-next-dual-gb10` profile now explicitly labels its earlier deployment recommendation **withdrawn**.

Historical bounded measurements on two ASUS Ascent GX10 / GB10 nodes over direct RoCEv2 were strong:

- no NEXTN, overlap disabled: about 18–20 tok/s;
- NEXTN 3/1/4, eager, overlap disabled: 41.60 / 42.39 / 42.86 tok/s;
- 16,384-token continuous generation: 48.01 tok/s;
- after a separate streaming-disconnect repair, 28,672-token generation: 52.76 tok/s.

Those numbers remain useful performance evidence, but they are no longer deployment-quality evidence. The same eager/no-overlap profile later failed under real multi-turn re-prefill traffic with:

- no client-disconnect precursor;
- one running request and an empty queue;
- CUDA Graph disabled;
- KV/token-pool utilization around 10%;
- both ranks reporting no OOM kill;
- invalid sampling probabilities followed by CUDA device-side assert / Xid 43, TP/NCCL termination, and container restart.

The repository therefore now fails closed unless the withdrawn profile is explicitly enabled for isolated research.

Source: https://github.com/hellojiaru/qwen38-flash-next-dual-gb10

### Qualification lesson

A persistent coding-agent qualification cannot stop at NIAH plus one long continuous generation. Add repeated long-context transitions:

- cache restore -> suffix prefill -> decode;
- tool call -> tool result append -> re-prefill -> decode;
- middle edit / compaction -> restore -> continuation;
- alternating short and long turns;
- stream disconnect/reconnect tests **and** equivalent no-disconnect soaks;
- several agents entering prefill/decode transitions at different times.

The important failure class is state-transition correctness after many turns, not merely maximum context length.

## Flash-Next / Apple: Metal radix TOP_K merged

llama.cpp PR #28073 merged a Metal radix `TOP_K` implementation modeled after the earlier Vulkan QSA work.

Reported M2 Ultra operator microbenchmarks show large improvements specifically on long, multi-row shapes, for example:

- `[131072,16]`, k=16: 14.48 -> 32.57 GB/s (`2.25x`);
- `[16384,16]`, k=16: 9.32 -> 17.16 GB/s (`1.84x`);
- `[24576,16]`, k=16: 10.37 -> 23.03 GB/s (`2.22x`);
- `[32768,16]`, k=16: 11.16 -> 27.11 GB/s (`2.43x`);
- `[200000,16]`, k=16: 14.84 -> 26.42 GB/s (`1.78x`);
- `[200000,16]`, k=400: 6.77 -> 26.64 GB/s (`3.93x`).

Source: https://github.com/ggml-org/llama.cpp/pull/28073

This is a kernel receipt, not a Flash-Next model-level receipt. Still, it changes the engineering order: before building a custom Apple TOP_K/indexer kernel, profile Flash-Next again on a llama.cpp baseline containing the merged radix path.

Related same-day Metal tuning also added fresh FA-vector tables for base M1 and M1 Ultra. M1 Max already had device-specific FA rows, so these merges are evidence of active M1-family backend tuning, not a new M1-Max full-model speed claim.

Sources:
- https://github.com/ggml-org/llama.cpp/pull/28078
- https://github.com/ggml-org/llama.cpp/pull/28088

## Qwen3.8-27B external state

No change.

The Layr-Labs `qwen-3.8-mtp-challenge` frontier remains:

`3.7291100105909`

PR #1481 remains the newest visible submission and still has no Apple-Silicon timing receipt in its submission note.

Source: https://github.com/Layr-Labs/qwen-3.8-mtp-challenge/pull/1481

### P69 decision

- keep the P69B12 exact-Q8 ruler untouched;
- proceed to P69B13 using existing profiling/census data;
- do not reopen P69B8, P69B9, or P69B10-C from these external results.

## DeepSeek-V4-Flash-0731 / DS4

No newer 0731 distributed throughput result supersedes the prior watch.

The important measured topology result remains:

- target-only tuned TP can win when enough useful compute exists between synchronization points;
- DSpark multi-row TP verification was measured net-negative on the tested hardware because per-layer exchange cost overwhelmed the speculative benefit;
- coarse layer-pipeline verification can amortize one multi-row span instead.

Current DS4 documentation also reinforces that speculative policy is hardware-dependent at non-zero temperature: predictable-code gains can survive on faster verification hardware while slower verification backends can regress. Treat speculation depth/gating as a measured per-platform policy, not a model constant.

Sources:
- https://github.com/antirez/ds4/pull/835
- https://github.com/antirez/ds4/pull/861

## Revised dual-M1 Flash-Next bring-up order

The performance target is unchanged; the qualification bar is higher.

1. single-M1 target-only baseline and M1/M2 FP16-activation A/B;
2. PP2 target-only over TB4, exact long-turn and cache-transition correctness;
3. continuous batching with 2–5 target-only agents;
4. context/ngram wide verification under the same concurrency;
5. prove sequence-isolated recurrent/PLE/QSA rollback with split-replay tests;
6. only then enable native distributed MTP for multiple agents;
7. soak repeated tool-use / re-prefill / compaction transitions, not just one long generation;
8. re-profile Apple QSA/TOP_K after the merged Metal radix kernel before custom kernel work.

None of these findings lowers the single-stream Flash-Next feasibility assessment. They do lower confidence in assuming that a B1-native-MTP implementation is automatically production-safe under 3–5 concurrent persistent agents.
