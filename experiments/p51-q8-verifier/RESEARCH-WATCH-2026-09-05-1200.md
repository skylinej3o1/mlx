# External runtime research watch — 2026-09-05 12:00 ET

Starting freshness boundary: `d29653cc19cbab780444fe6e12230166953cde5a` / 2026-09-05 09:05:17 UTC.

This pass is **material but does not move any canonical TG / PP target or confidence**. The strongest new evidence is about recurrent-session correctness, per-slot MTP sizing, DS4 prefill benchmark semantics, persistent-cache identity and a separate non-bit-exact M1/M2 FP16 serving lane.

Canonical planning centers remain:

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

`RESEARCH-TARGETS.md` remains unchanged and authoritative.

---

## Fresh / material

### llama.cpp #28433 — MTP draft context can be sized from total server context instead of per-sequence context

Created after the boundary at 09:59:58 UTC. Qwen3.8-27B on Strix Halo / Vulkan with `--parallel 3` showed a clean ablation around a draft-MTP context-sizing error:

- `--ctx-size 786432`, parallel 3, no unified KV + MTP: every request fails at prompt/decode transition;
- same total context with n-gram only: works, reported 12.8 tok/s and 99.99% cache reuse;
- total context 393216 + MTP: works, reported 24 tok/s;
- 524288 unified + MTP: works, reported 23.7 tok/s.

The reported code path assigns `cparams.n_ctx = llama_n_ctx(ctx_tgt)` despite the nearby comment stating that the draft should hold the target context **per sequence**. The proposed correction is to use `llama_n_ctx_seq(ctx_tgt)`.

This is not Apple-M1 or 5070 throughput evidence. The failure class transfers directly to the planned multi-agent server: **draft/MTP memory and context sizing must be certified per slot, not inferred from the aggregate server context**. A large aggregate `--ctx-size` must not silently multiply draft state with concurrency.

### llama.cpp #28425 update — non-spec recurrent partial rollback is a dedicated multi-turn correctness gate

The issue itself predates the cutoff, but the post-cutoff update narrows and strengthens the diagnosis. For Qwen4Exp/recurrent architectures, ordinary non-speculative prompt-cache partial trims can request `seq_rm(p0 > 0)` while `n_rs_seq` remains zero, because rollback depth is currently populated through speculative configuration.

The fresh controlled comparison reports:

- standard non-recurrent transformer under the same tight-memory growing-conversation protocol: stable through ~30 turns / ~8K tokens, free VRAM flat after settling;
- hybrid/recurrent model: degraded to 2-8 output tokens per turn within a handful of turns;
- a separate ~2-3 MB/request HIP-only memory drift on unrelated requests was identified as a confound and explicitly separated from the recurrent rollback problem.

The issue also reports an unchecked failed partial trim can produce a GPU memory fault on a subsequent shared-prefix request.

**Policy:** before enabling normal multi-turn `cache-prompt` reuse on Flash-Next, certify non-spec recurrent partial rollback independently of MTP: second-turn shared-prefix trim, long growing conversation, exact state/output reference and memory plateau. A safe MTP path does not prove the ordinary no-spec session path is safe.

### DS4 #952 update — AProjQ4 prefill effect is a function of fresh increment size, not just context

Fresh 10:06:34 UTC follow-up resolves the prior PP-attribution ambiguity with a 2x2x2 factorial run (192 measurements) plus 108-run isolation.

At context 8192, commit and `--gen-tokens` were null factors: four cells gave approximately +2.53% to +2.87% Q4-vs-Q8 with overlapping intervals. The real distinction is `prefill_tokens` / increment size because `ds4-bench` reuses the existing KV as a sweep advances.

Reported AProjQ4 vs AProjQ8 prefill effects:

- 2,048 fresh tokens at ctx 2,048: **+5.01%** [4.64, 5.38];
- 2,048 fresh at ctx 8,192: **+2.53%** [2.10, 2.95];
- 8,192 fresh at ctx 8,192: **+0.41%** [0.16, 0.66];
- 16,384 fresh at ctx 32,768: **-0.08%** [-0.44, 0.27];
- 32,768 fresh at ctx 65,536: **-0.15%** [-0.48, 0.19].

Decode remains the strong AProjQ4 result in that thread: about **+13.9%** on the measured GB10 configuration.

**Policy:** `context`, `prefill_tokens`, step/increment size and prefill cap are separate benchmark dimensions. For the exact dual-M1 AProjQ4 test, report both cold/full-prompt PP and small incremental agent-turn PP; never pool equal-context rows with different fresh work. This also means AProjQ4 may be more useful for incremental agent turns than its large-cold-prefill parity suggests.

### DS4 #982 — prior text-only tool-observation diagnosis now has a focused fix and physical Metal validation

Created after the boundary at 09:38:31 UTC. The PR formalizes the earlier #973/#969 diagnosis: text-only DeepSeek tool observations were routed through a multimodal append path, the append failed, and the failure was misread as context overflow, triggering pointless compaction and eventually `context full after compaction` at only ~2K tokens.

The fix sends image-free tool observations through the plain tool-message path and retains the multimodal path only when images are present. Reported physical validation on Apple M3 Ultra / Metal / text-only DeepSeek V4 Flash completes a forced bash-tool round trip cleanly.

**Policy:** DS4 agent qualification explicitly tests text-only tool execution/observation before interpreting any compaction or context-full error as capacity pressure.

### DS4 #983 — tokenizer fingerprint makes persisted KV checkpoints self-healing across tokenizer changes

Created at 11:43:28 UTC. A production long multimodal agent session reportedly hit **29 consecutive turns** that each reloaded the same stale checkpoint and re-prefilled ~38K tokens because tokenizer behavior had changed while the text key remained the same.

The PR adds a behavioral tokenizer fingerprint to checkpoint trailers and rejects a mismatched checkpoint before reading its payload. On M5 Max the author reports:

- full 451K-token stamped checkpoint restored with only 38-token re-prefill when tokenizer identity matched;
- a synthetic tokenizer skew rejected old stamped files immediately and allowed the normal fallback/store path to rewrite a valid checkpoint.

This is DS4-specific implementation evidence, but the product lesson transfers strongly: **persistent session/cache artifacts in the turnkey kit need behavioral tokenizer/model/runtime identity, not just a text key or filename.** Stale state should fail closed and self-heal.

---

## Fresh update / M1-family serving evidence — separate approximate lane

### oMLX #3277 — M1/M2 native-FP16 activation recast is a large physical gain but changes numerics

The PR was refreshed/rebased post-cutoff (current update 14:37 UTC); the measurement work itself originated earlier and is treated here as a newly surfaced / updated data point rather than a clean fresh-day experiment.

On **Apple M1 Ultra 128 GB**, Qwen3.8-Flash-Next `oQ4e-mtp`, recasting only non-quantized BF16 leaves to FP16 while leaving quantized U32 payloads unchanged reportedly produced:

- rewrite decode: **28.29 -> 32.26 tok/s (+14.0%)**;
- novel decode: **22.89 -> 24.07 tok/s (+5.2%)**;
- cold unique-prompt prefill: **313.2 -> 500.2 tok/s (+59.7%)**;
- per-cycle cost down about 8-9%, with draft acceptance broadly flat in the measured scenarios.

The author explicitly states output is **not bit-identical** to BF16 because FP16 and BF16 round differently, although the reported quality prompts remained correct/coherent. The option is off by default and intended only for M1/M2, where BF16 arithmetic is described as emulated.

**Promotion:** create a separate `M1/M2 activation-FP16` serving lane after the exact baseline. It requires quality/eval and long greedy/agent regression certification; it does **not** alter P69 exactness and does not move the canonical exact-runtime Flash or 27B targets. It is nevertheless one of the strongest M1-family performance mechanisms seen so far and deserves an early A/B on the actual M1 Max boxes once baseline correctness is frozen.

---

## Backfill / long-context Apple mechanisms worth adding to the Flash test plan

### oMLX #3455 — reserve QSA indexer capacity from the known prompt horizon

Same-day pre-cutoff backfill. On a 128-GB Apple Silicon Qwen4Exp hybrid serving test, the generic indexer doubling policy reportedly grew a 205K prefill cache to 393,216-token capacity (beyond the 262,144 model horizon), including a +12.25-GB resident spike around 196K.

Reserving the known request horizon changed the reported cold 205K case from rejection/model unload to completion, with peak physical footprint **102.17 -> 92.37 GB**, indexer resident **10.46 -> 6.77 GB**, and swap **+6.2 GB -> ~0**. A warm 212K prefix-hit request went **115 -> 99 s**.

Transfer: for Flash long-context bring-up, pre-size/reserve QSA indexer capacity from the known per-request horizon rather than doubling opportunistically at the deepest/highest-pressure point.

### oMLX #3456 — recurrent boundary checkpoints can dominate long-context memory

Same-day backfill. On a 128-GB Apple Silicon Qwen4Exp hybrid model, the report measured 115.6 MB per recurrent boundary checkpoint; a 234K prefill retained 113 checkpoints / 12.06 GB. Capping retained checkpoints at four on a 261K prompt reduced reported resident snapshot memory **13.68 -> 0.43 GB** and peak physical footprint **99.12 -> 85.63 GB**, with about +2% wall-time cost.

In a measured multi-turn run, the budgeted configuration reused 98,304 tokens on turn 2 and 210,944 on turn 3; turn 3 took 24 s versus 207 s in the comparison where pressure prevented useful reuse. Divergence from a pruned boundary was also compared against a cache-disabled greedy reference and reported byte-identical after re-prefilling from the nearest retained checkpoint.

Transfer: recurrent checkpoint density is a first-class memory/reuse knob. More checkpoints are not automatically better if their resident cost evicts the KV/prefix chain they are meant to protect. Test bounded, uniformly spaced stage-local snapshots as a long-context agent lane rather than retaining every boundary by default.

---

## Exact-rig no-change confirmations

- **Dual-M1 Flash:** llama.cpp #27993 has no post-cutoff comment; no new sustained exact 2x M1 Max64/TB4 TG receipt or completed long-context exact result surfaced.
- **Dual-M1 DS4-0731:** #922 has no post-cutoff comment and still provides no exact sustained generated-token denominator. #952's fresh work changes benchmark interpretation, not an M1 rate ruler.
- **RTX 5070 Ti Qwen3.8-27B:** `aipruner/qwen3.8-3bit-test-in-16GB-GPU` still has `pushed_at=2026-08-20T19:16:50Z`; no new exact-card receipt.
- **Apple DSpark:** `ARahim3/mlx-dspark` still has `pushed_at=2026-09-01T10:54:45Z`.
- **M1 Max64 Qwen3.8-27B:** no new exact single-M1-Max serving receipt surfaced. The M1-Ultra activation-FP16 result is different hardware and numerically approximate.

---

# Consequences by lane

## Dual-M1 Flash-Next

Updated qualification order:

1. pin/certify a known llama.cpp baseline on both Macs;
2. plain exact **PP2/layer-owned** baseline; TP2 control;
3. **ordinary no-spec multi-turn recurrent rollback / partial-prefix trim gate**;
4. PLE residency/page-cache/direct-read A/B;
5. sparse-QSA wide-prefill A/B;
6. neighboring-row selected-block reuse after sparse-QSA passes;
7. QSA indexer-horizon reservation / no-mid-prefill-doubling A/B at long context;
8. recurrent boundary-checkpoint density / retention-budget A/B;
9. pooled QSA-prefix retention / rollback correctness;
10. Metal target-op batch-width invariance with production tensor/scale layouts;
11. singleton MTP state snapshot/verify/commit A/B;
12. **verify MTP draft context is per-slot/per-sequence across parallel=1/2/3/4 and large aggregate ctx**;
13. mismatched-length concurrent pure-prefill state-isolation gate;
14. adversarial parallel-MTP slot isolation;
15. separate **M1/M2 FP16-activation approximate lane** with quality/eval certification;
16. compiled-decode B2/B4, workload-derived cache/session tuning and long-prefill-during-decode stress.

Turnkey/persistent-session qualification additionally stamps persistent state with tokenizer/model/runtime identity and rejects incompatible artifacts rather than repeatedly restoring stale state.

Canonical center remains **40 TG / 400 cold PP**.

## Dual-M1 DS4-0731

Keep PP2/layer ownership primary and TP2 control. AProjQ4 remains primary candidate.

AProjQ4 PP must now be reported in at least two distinct modes:

- full/cold prompt PP at fixed fresh-token work;
- small incremental agent-turn PP at fixed 2K/4K-scale fresh increments.

Do not infer a general PP advantage from one sweep geometry. Tool-observation qualification now has a focused upstream fix (#982), and persisted KV/session qualification should include tokenizer-fingerprint invalidation/self-healing (#983).

Canonical center remains **15 TG / 180 cold PP**.

## Single M1 Max64 Qwen3.8-27B

No exact-target movement. Preserve P69 separation: **P69B12 frozen/promoted; P69B13 next from existing profiling only**.

After the exact/native baseline, explicitly test an **activation-FP16 approximate serving lane** because the M1-Ultra result is strong enough to merit physical M1-Max qualification. Do not merge its numerics into P69 exactness or the 110-PP exact-runtime center without a separate target recalibration.

Canonical center remains **25 TG / 110 native cold PP**.

## RTX 5070 Ti16 Qwen3.8-27B

No target change. Keep fully resident Q3_K_XL + native MTP, DFlash control, CUDA linked-runtime/driver provenance, ubatch/prompt-shape stability, draft-cache net-memory accounting, MTP-head quant and small-N verifier checks. When serving parallel sessions, inherit the new general rule that draft context/state must be sized per sequence rather than from the aggregate server horizon.

Canonical center remains **120 TG / 250 cold PP**.

---

# Standing architecture / certification decisions added or strengthened this pass

- Flash and DS4 dual-M1 experiments remain **PP2/layer ownership first, TP2 control**.
- **Ordinary non-spec recurrent rollback is its own certification surface.** MTP rollback passing does not prove growing multi-turn prompt-cache reuse is safe.
- **MTP/draft context sizing is per sequence/slot.** Aggregate server context and concurrency must not silently multiply draft memory/state.
- **Cold/full PP and incremental-agent PP are separate metrics.** Equal context does not mean equal work; record fresh `prefill_tokens`, step size and prefill cap.
- **AProjQ4's measured PP benefit is chunk-size dependent** in the fresh GB10 data; its decode benefit remains much stronger.
- **M1/M2 FP16-activation recast is an approximate serving lane, not exact-runtime evidence.** Quality certification is mandatory.
- QSA indexer capacity should be reserved from known request horizon where possible; avoid late doubling at peak memory pressure.
- Recurrent checkpoint density is a memory/reuse tradeoff; bounded snapshots may preserve more useful prefix state than retain-all.
- Persistent KV/session artifacts should carry tokenizer/model/runtime identity and fail closed/self-heal on mismatch.
- Text-only DS4 tool observations must use the text path; a compaction error is not proof of actual context pressure.
- Production-layout fidelity, driver/runtime provenance and target-op width invariance remain required for low-level exactness/stability claims.
- Stronger/different hardware and non-bit-exact mechanisms do not move exact-machine targets by themselves.
- P69 exact verifier work remains isolated from serving/runtime experimentation.
