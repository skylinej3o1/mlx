# Qwen3.8-Flash-Next late Aug-28 field delta

Status: **FRESH FIELD EVIDENCE / follow-up to `QWEN38_FLASH_NEXT_AUG28_FIELD_DELTA.md`**

Updated: 2026-08-28 evening ET.

This note captures developments that appeared after the earlier Aug-28 Flash-Next field checkpoint. It is intentionally additive rather than rewriting the earlier chronology.

## Executive delta

1. **Batched Lightning MTP is now being exercised under real multi-row concurrency.** oMLX PR #3265 adds an opt-in depth-1 speculative cycle across a whole decode batch instead of dropping to plain batching when two or more requests are active. On Qwen3.8-Flash-Next oQ4e / M3 Ultra, the author reports ~56% batched acceptance versus ~61% single-stream and roughly **+70-90% per-session throughput for four concurrent sessions versus plain batched decode**. The implementation includes a per-row GDN rollback channel; 449 rollback rows were reported as exact with zero state pollution.
2. **Flash-Next imatrix/sensitivity calibration no longer requires anything close to full-model residency.** oMLX PR #2161 extends layer-streaming oQe calibration to `qwen4_exp`. A full fused imatrix+sensitivity collection over the ~335 GB BF16 Flash-Next checkpoint reportedly ran with roughly **21 GB active memory** in about 50 minutes while preserving exact expert-routing counts and bit-identical accumulated imatrix statistics on the parity fixture. This makes custom architecture-aware quant calibration practical on much smaller Apple machines.
3. **The SSD-PLE batching result now has a stricter cold-cache protocol.** PR #3235 reran with fresh processes, `sudo purge`, alternating builds, empty prefix cache and model-load time excluded. Reported cold prefill moved from **213.1 -> 843.8 tok/s at 1K**, **239.8 -> 1043.3 at 4K**, and **282.4 -> 734.2 at 16K**. The isolated cold gather fell from roughly 145-181 us/row to 22.4-23.4 us/row with essentially unchanged resident memory.
4. **Exact API token reconstruction matters to prefix-cache economics.** oMLX PR #3268 found that collapsing Qwen's empty no-thinking marker to `None` changed the next-turn token sequence, destroying prefix reuse. Preserving the empty reasoning content restored a 2,048-token cache hit; a reported 15-case file-localization run recovered that final-pass cache hit in all 15 cases.

## 1. Batched depth-1 MTP for concurrent agents

Source:
- https://github.com/jundot/omlx/pull/3265

The important architectural change is not merely another MTP benchmark. Existing serving behavior could deactivate MTP on multi-row decode steps. The proposed path instead performs one speculative candidate per active row, verifies the batch, and then rolls recurrent state back independently for rows that reject.

Reported Flash-Next / M3 Ultra result:

- single-stream acceptance: ~61%;
- batched acceptance: ~56%;
- four concurrent sessions: ~70-90% higher per-session throughput than plain batching;
- exact GDN restoration verified on 449 rollback rows.

This is depth 1 only, opt-in and not yet a final production policy. It nevertheless establishes that speculative decoding and continuous batching do not have to be mutually exclusive.

### MXFORGE implication

For the intended orchestrator/subagent server, treat batched speculation as a first-class later workstream. Do not optimize only batch-1 MTP and assume the gain survives concurrency automatically.

The two-M1 distributed problem remains separate: a correct single-node batched verifier does not solve Thunderbolt TP/PP verifier communication.

## 2. Layer-streamed Flash-Next imatrix calibration

Source:
- https://github.com/jundot/omlx/pull/2161

The new `qwen4_exp` path streams one decoder layer at a time through the calibration corpus rather than holding the full target or a whole-model proxy resident.

Reported real-checkpoint result:

- source checkpoint: ~335 GB BF16 Qwen3.8-Flash-Next;
- full fused imatrix + sensitivity collection;
- adaptive escalation to 1,024 samples / 8 rounds;
- about 50 minutes;
- ~21 GB active memory;
- exact expert-routing counts in parity validation;
- bit-identical `in_sum2` imatrix accumulation;
- fused qdq sensitivity within 1e-6 of the resident reference path.

The implementation also keeps the giant PLE mmap-backed and allows the n-gram table to be preserved separately from core quantization.

### MXFORGE implication

This materially strengthens the case for producing a custom coding/agent-calibrated Flash-Next quant instead of depending entirely on third-party allocation recipes.

Preferred eventual process:

```text
official BF16 checkpoint
  -> coding/agent calibration corpus
  -> layer-streamed imatrix + sensitivity
  -> architecture-aware neural-trunk allocation
  -> separately quantized Q5_1/~6-bit SSD PLE
  -> frozen coding/agent quality certification
```

A single 64 GB M1 Max should have ample capacity for the reported calibration residency envelope, subject to local runtime validation.

## 3. SSD-PLE result: stricter rerun

Source:
- https://github.com/jundot/omlx/pull/3235

Updated interleaved cold-process measurements on M5 Max 128 GB:

| Prompt | main | batched/advised gather | speedup |
|---:|---:|---:|---:|
| 1,024 | 213.1 tok/s | 843.8 tok/s | 3.96x |
| 4,096 | 239.8 | 1043.3 | 4.35x |
| 16,384 | 282.4 | 734.2 | 2.60x |

The isolated cold gather reports roughly 145-181 us/row on main versus 22.4-23.4 us/row after batching/advising, while resident memory stayed about 69.6 GB in both arms.

The lower relative gain at 16K is itself useful: early prompt chunks warm rows that later chunks reuse, so cold PLE cost amortizes within a long prompt.

This strengthens the earlier conclusion that serial per-row page faults, not useful SSD bandwidth, were the major avoidable cold-prefill penalty.

## 4. No-thinking marker and exact prefix reuse

Source:
- https://github.com/jundot/omlx/pull/3268

Qwen's no-thinking generation prefix contains an empty reasoning marker. If an OpenAI-compatible server converts that empty content to `None`, a stateless client cannot echo the same marker on the next turn and the rendered prompt tokens change.

Reported live Flash-Next behavior:

- before fix: divergence at the no-thinking marker and final `cached_tokens=0`;
- after fix: exact rerender and `cached_tokens=2048`;
- 15/15 file-localization cases restored the 2,048-token final-pass cache hit.

### MXFORGE implication

Prefix caching must be certified at the token-rendering/API boundary, not only inside the model cache implementation. For agent servers, preserve semantically empty but tokenically significant template fields whenever exact continuation is expected.

## Updated priority delta

Relative to the earlier Aug-28 note:

1. Keep exact QSA + SSD-PLE planner as first-tier runtime work.
2. Add **custom layer-streamed imatrix calibration** as a first-tier quant-enablement task.
3. Add **batched MTP** to the server-level plan after batch-1 verifier economics are stable.
4. Add exact prompt-template/API round-trip tests to prefix-cache certification.
5. Continue to treat distributed MTP as unqualified until measured on the two-M1 topology.
