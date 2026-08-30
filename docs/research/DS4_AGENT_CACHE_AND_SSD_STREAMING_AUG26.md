# DwarfStar / DS4 agent-cache continuity and SSD-streaming refresh

Status: **CORE / runtime architecture evidence**

Updated: 2026-08-26

## Sources

Fresh field report:

- https://www.reddit.com/r/LocalLLaMA/comments/1vx4jg9/dwarfstar_cache_misses_down_from_50_to_0/

Relevant DS4 PRs:

- visible tool-context checkpoints / live KV continuity:
  https://github.com/antirez/ds4/pull/789
- multi-slot routing that preserves reusable live KV:
  https://github.com/antirez/ds4/pull/765
- packed expert sidecar for SSD streaming:
  https://github.com/antirez/ds4/pull/848
- next-layer router lookahead expert prefetch:
  https://github.com/antirez/ds4/pull/849

## 1. Agent cache continuity can dominate raw prefill optimization

The Reddit field report says the author's cache-miss rate fell from roughly 50% to approximately zero in their workload, allowing them to disable the cold cache. They report that the previous fallback was generating roughly **1 TB/day of SSD writes**.

The same post reports approximate current throughput of:

- ~40 tok/s decode / ~600 tok/s prefill near zero context;
- ~32 tok/s decode / ~260 tok/s prefill around 90K context.

Treat those throughput values as field-report context, not a controlled MXFORGE benchmark.

The important systems result is avoiding unnecessary re-prefill and disk checkpoint traffic.

## 2. Why agent turns miss live KV even when the conversation looks identical

Agentic traffic commonly has multiple representations of the same logical turn:

- exact sampled assistant text;
- hidden reasoning;
- tool-call serialization;
- client-normalized JSON;
- chat-template reconstruction;
- BPE-boundary differences;
- retries / stream interruption;
- canonicalized visible transcript.

If the engine only asks whether the next client-rendered token sequence exactly matches the sampled token tail, a logically continuous conversation can fall off the live KV frontier.

Failure mode:

```text
turn N generated
    ↓
client reconstructs turn
    ↓
small token/serialization mismatch
    ↓
live KV rejected
    ↓
disk restore or cold re-prefill
    ↓
large avoidable latency + SSD traffic
```

## 3. DS4 visible checkpoints

PR #789 extends the visible-checkpoint idea to chat / Anthropic tool-call flows.

Core principle:

> Bind a predictable visible continuation to the authoritative live KV frontier, instead of requiring the next client replay to reproduce every sampled/internal token byte-for-byte.

The PR also preserves the live frontier across certain streaming errors and stores waypoints through tool-call periods, reducing the chance that an interrupted agent turn falls back to a near-total re-prefill.

MXFORGE action:

- treat transcript identity and KV identity as first-class state;
- preserve authoritative sampled text / tool serialization;
- store an explicit visible-continuation key;
- expose why a cache continuation hit or missed;
- never silently rebuild 30K-100K context when a reusable live frontier exists.

## 4. Multi-slot session affinity

PR #765 fixes a second failure mode: a subagent can steal the main agent's KV slot simply because it shares a long prefix.

The correct routing question is not "which slot shares the longest prefix?" but:

> **which slot can actually reuse its current KV state for this exact request?**

The PR's small reproduction shows the returning main agent going from a full re-prefill path to a tiny suffix-only update when the subagent is routed to an empty slot instead of overwriting the main slot.

At very long context this becomes enormous. The PR notes a ~120K-token cold prefill on its tested system taking minutes, while live-memory continuation only needs the new suffix.

MXFORGE scheduler rule:

1. prefer an exact reusable live slot;
2. otherwise prefer an empty slot;
3. evict only when necessary;
4. make victim choice staleness-aware;
5. disk snapshots are recovery capacity, not the normal hot path.

## 5. SSD expert streaming: layout matters before prediction

PR #848 addresses routed-expert SSD locality.

Ordinary GGUF layout stores each MoE expert's gate/up/down slices in three widely separated tensors. One cache miss therefore causes three distant SSD reads.

The PR creates an optional packed sidecar:

```text
expert 0: gate | up | down
expert 1: gate | up | down
...
```

No weights are requantized or numerically changed; only disk placement changes.

Reported M4 Max 36GB / DeepSeek V4 Flash result:

- +10.7% generation throughput;
- identical miss count;
- byte-identical output.

This is strong evidence for a general rule:

> **Optimize storage layout around the runtime fetch unit.**

A fast NVMe drive cannot compensate for pathological physical layout if each logical object is fragmented into distant extents.

## 6. Predictive expert prefetch only worked after layout was fixed

PR #849 adds one-layer lookahead routing on top of the packed layout.

During layer L compute, a background thread runs layer L+1's router using a slightly stale hidden state and prefetches predicted experts into otherwise-idle SSD windows.

Reported observations:

- top-4 guesses covered about 46% of future misses in the measured workload;
- packed-layout + lookahead: ~+5.2% generation;
- lookahead without packed layout: ~5.5% slower despite lower average read latency.

This is a particularly valuable negative result.

Interpretation:

The predictor is only useful when the demand-read layout first creates genuine idle I/O windows. With fragmented expert reads, speculation competes with required reads and burns bandwidth.

Therefore:

```text
1. fix physical layout
2. measure I/O idle windows
3. prefetch only into slack
4. never let speculative reads evict/block demand reads
```

The PR also uses predicted near-future experts as **eviction protection**, preventing the cache from throwing away an expert immediately before reuse.

## 7. Hash-routed vs learned-routed memory

PR #849 notes a useful distinction:

- learned MoE router: next-layer expert set must be predicted;
- hash-routed layer: expert addresses can be known exactly once token identity is known.

This directly connects to the Flash-Next / Engram research note.

For deterministic N-gram memory, MXFORGE should prefer exact address prefetch over learned prediction whenever possible.

## 8. Unified runtime principle

The recent DS4 work suggests one project-level principle:

> **If future state or future memory addresses are knowable early, move work off the critical path.**

Examples:

```text
Agent KV
visible next transcript known
    -> preserve / bind live KV
    -> avoid re-prefill

MoE weights
next-layer experts partly predictable
    -> prefetch during current-layer compute

Hash / N-gram memory
lookup addresses deterministic after token IDs are known
    -> exact prefetch + hot cache
```

This principle is broader than any single model/runtime.

## 9. MXFORGE telemetry to add eventually

Agent/cache telemetry:

- live-KV hit rate;
- miss reason: token mismatch / slot eviction / template drift / unavailable state;
- tokens reused;
- tokens re-prefilled;
- avoidable re-prefill estimate;
- disk KV bytes read/written;
- per-session slot ownership and age.

SSD expert/memory telemetry:

- cache hit/miss by layer/expert;
- reads per token;
- bytes per miss;
- physical extents per logical fetch;
- demand vs speculative reads;
- useful/wasted prefetch ratio;
- prefetch lead time;
- SSD busy/idle fraction;
- page-cache hits;
- eviction-before-reuse events.

## Promotion rule

Do not import headline percentages directly across hardware.

Promote the **mechanisms** now:

- live visible-checkpoint continuity;
- reusable-slot-aware session routing;
- storage layout aligned with logical fetch objects;
- slack-aware predictive prefetch;
- eviction protection for near-future objects;
- SSD as cold capacity / recovery rather than routine hot-path traffic.

Reproduce all throughput effects on the actual MXFORGE M1 / two-M1 / CUDA target before promoting numbers.
