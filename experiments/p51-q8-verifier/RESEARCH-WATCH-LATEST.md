# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical research state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Read the canonical performance targets and planning-confidence ladders:

   `experiments/p51-q8-verifier/RESEARCH-TARGETS.md`

   **This file is authoritative for TG / PP working targets and confidence.** Do not reconstruct targets from older watch-note prose.

3. Read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-05-1200.md`

   **The 12:00 note is authoritative for current promotion level, ordinary recurrent-session rollback, per-slot MTP context sizing, DS4 fresh-prefill benchmark semantics, M1/M2 FP16 activation experimentation and persistent-cache identity.**

4. Because `RESEARCH-STATE.md` was last consolidated at 05:30 ET on 2026-09-02, retain the dated deltas newer than that point when reconstructing the evidence chain. The most recent relevant sequence is:

   - `RESEARCH-WATCH-2026-09-04-0115.md` — compiled-decode correction / hidden ANE-bank accounting;
   - `RESEARCH-WATCH-2026-09-04-0625.md` — PLE residency, DS4 command-buffer/OS, Blackwell ubatch and cache granularity;
   - `RESEARCH-WATCH-2026-09-04-0915.md` — v0.4.0-era baseline, parallel-MTP isolation, SSD-expert streaming and MTP-head quant;
   - `RESEARCH-WATCH-2026-09-04-1550.md` — PP-vs-TP structural evidence, production cache-granularity failure and CUDA provenance;
   - `RESEARCH-WATCH-2026-09-04-1840.md` — stable v0.4.0 pin, modality-agnostic KV reuse, DS4 tool-observation correction and MTP draft-cache VRAM;
   - `RESEARCH-WATCH-2026-09-04-1930.md` — Flash MTP commit semantics, concurrent-PLE state isolation, Apple recurrent kernels and decoupled cache geometry;
   - `RESEARCH-WATCH-2026-09-05-0400.md` — neighboring-row QSA gather reuse, Metal `MUL_MAT` width exactness and DS4 fixed-work PP;
   - `RESEARCH-WATCH-2026-09-05-0500.md` — production-layout invariance correction, low-level runtime provenance and Strix-Halo AProjQ4 smoke;
   - `RESEARCH-WATCH-2026-09-05-1200.md` — recurrent multi-turn rollback, per-slot draft context, chunk-size-dependent AProjQ4 PP, M1/M2 FP16 activation lane and persistent-state identity.

5. Also read `RESEARCH-MINING-2026-09-01-IQ-PANEL.md` when looking for portable kernel candidates.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

**The 12:00 pass moves no row.** It adds strong architecture/correctness/memory evidence but no new sustained physical receipt from the four target rigs.

Important qualifiers:

- Flash retains the B1 short/medium, ~128K B1 and B2-B4 aggregate ladders in `RESEARCH-TARGETS.md`.
- M1/M2 activation-FP16 is now a separate **approximate serving lane**; its outputs are not bit-identical to BF16 and it does not alter P69 or exact-runtime targets.
- 5070 targets require full residency and measured net VRAM/context headroom.
- DS4 remains conservative until exact sustained 0731 dual-M1 generated-token throughput is measured.

---

# Current newest evidence delta — 2026-09-05 12:00 ET

Starting freshness boundary: `d29653cc19cbab780444fe6e12230166953cde5a` / 2026-09-05 09:05:17 UTC.

## Fresh / material

### llama.cpp #28433 — aggregate server context can over-size MTP draft state

Fresh Strix-Halo/Vulkan Qwen3.8-27B ablation reports draft-MTP failure with `--parallel 3` at a very large aggregate context while the same context works without MTP and smaller aggregate contexts work with MTP. The reported code uses total `llama_n_ctx(ctx_tgt)` where the comment describes per-sequence sizing; `llama_n_ctx_seq()` is proposed instead.

**Promotion:** multi-agent MTP certification must prove draft context/state is sized per sequence/slot for parallel=1/2/3/4 and large aggregate context. Do not infer draft memory from per-slot target context unless the implementation actually uses it.

### llama.cpp #28425 update — ordinary no-spec recurrent rollback must be certified separately

Fresh controlled follow-up narrows the issue to growing conversations on recurrent/hybrid architectures: the standard-transformer control remains stable while the hybrid/recurrent path degrades under the same tight-memory protocol. A separate HIP-wide few-MB/request drift was identified and removed from the recurrent attribution.

**Promotion:** before ordinary prompt-cache/session reuse on Flash-Next, test no-spec partial-prefix trims, second-turn shared-prefix reuse, growing multi-turn state correctness and memory plateau. MTP rollback correctness does not prove the ordinary session path.

### DS4 #952 update — AProjQ4 PP depends strongly on fresh prefill increment

Fresh factorial/isolation work shows commit, prompt file and generation coupling were not the prior discrepancy. `ds4-bench` advances through the context while reusing KV, so `prefill_tokens` / increment size changes the measured operation.

Reported Q4-vs-Q8 PP effects range from **+5.01%** at a 2K fresh first increment and **+2.53%** at 2K fresh / ctx8K, to approximately parity for 16K/32K fresh increments. Decode remains about +13.9% on the measured GB10 configurations.

**Promotion:** every DS4 PP receipt records context, actual fresh `prefill_tokens`, increment/step and prefill cap. Measure cold/full PP and incremental-agent PP separately. AProjQ4 may matter more for small agent turns than for large cold prefill.

### DS4 #982 — text-only tool-observation fix now has focused Metal validation

Fresh PR formalizes the earlier #973/#969 diagnosis: text-only DeepSeek tool observations could be sent through a multimodal path, fail, then be misreported as context overflow and trigger futile compaction. The focused fix restores the plain text tool-message path; M3-Ultra/Metal validation reports a complete bash-tool round trip.

### DS4 #983 — persisted KV checkpoints gain behavioral tokenizer identity

Fresh PR addresses a reported 29-turn stale-checkpoint loop where each turn reloaded the same incompatible state and re-prefilled ~38K tokens. Behavioral tokenizer fingerprinting lets mismatched state fail before payload load and be rewritten through normal prefill. M5-Max validation reports a matching 451K checkpoint restoring with only 38-token re-prefill and synthetic tokenizer skew self-healing correctly.

**Transfer:** persistent agent/session artifacts should carry tokenizer/model/runtime identity, reject incompatible state and recover automatically.

## Updated / newly surfaced M1-family lane

### oMLX #3277 — M1/M2 FP16 activation recast

Current PR update/rebase surfaced a strong M1-Ultra Flash-Next result. Recasting only non-quantized BF16 leaves to FP16 while keeping quantized U32 payloads unchanged reportedly gives:

- rewrite TG 28.29 -> 32.26 (+14.0%);
- novel TG 22.89 -> 24.07 (+5.2%);
- unique cold PP 313.2 -> 500.2 (+59.7%).

The author explicitly says output is **not bit-identical** to BF16. Treat this as a separate approximate/quality-certified M1/M2 serving lane. It is strong enough to A/B early after exact M1-Max baseline freeze but does not move the 40/400 Flash center, the M1-27B 25/110 exact center or P69.

## Same-day backfill promoted to long-context Flash test plan

### oMLX #3455 — reserve known QSA indexer horizon

On 128-GB Apple Silicon Qwen4Exp, opportunistic indexer doubling reportedly caused a +12.25-GB spike during a 205K prefill and overshot model context capacity. Reserving the known horizon reduced peak physical memory by ~9.8 GB and changed the cold case from rejection to completion; warm 212K prefix-hit wall time improved 115 -> 99 s.

### oMLX #3456 — budget recurrent boundary snapshots

On 128-GB Apple Silicon Qwen4Exp, retain-all recurrent checkpoints reached 13.68 GB at a 261K prompt. A four-checkpoint budget reduced that to 0.43 GB and peak physical memory by ~13.5 GB. The reported multi-turn case then retained deep prefix hits; greedy divergence tests re-prefilled from the nearest retained boundary and matched a cache-disabled reference.

**Transfer:** pre-size QSA indexers from known horizons; treat recurrent snapshot density as a memory/reuse tradeoff rather than retain-everything by default.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** llama.cpp #27993 has no post-boundary comment; no fresh sustained exact 2x M1 Max64/TB4 TG or completed long-context exact result surfaced.
- **Dual-M1 DS4-0731:** #922 has no post-boundary comment and no sustained generated-token denominator. #952 changes methodology, not M1 calibration.
- **RTX 5070 Ti 27B:** `aipruner/qwen3.8-3bit-test-in-16GB-GPU` remains `pushed_at=2026-08-20T19:16:50Z`.
- **Apple DSpark:** `ARahim3/mlx-dspark` remains `pushed_at=2026-09-01T10:54:45Z`.
- **M1 Max64 27B:** no new exact single-M1-Max receipt surfaced; the M1-Ultra FP16 result is different hardware and numerically approximate.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Qualification order:

1. pin/certify known llama.cpp baseline on both Macs;
2. exact **PP2/layer-owned** baseline; TP2 control;
3. **ordinary no-spec recurrent partial-prefix rollback / growing-session gate**;
4. PLE residency/page-cache/direct-read A/B;
5. sparse-QSA wide-prefill A/B;
6. neighboring-row selected-block reuse;
7. QSA known-horizon reservation / no late doubling at long context;
8. recurrent boundary-snapshot retention-density A/B;
9. pooled QSA-prefix/session restore correctness;
10. Metal target-op batch-width invariance using production layouts;
11. singleton MTP recurrent snapshot/verify/commit A/B;
12. **per-slot MTP draft-context sizing under parallel=1/2/3/4 and large aggregate ctx**;
13. mismatched-length concurrent pure-prefill state isolation;
14. adversarial parallel-MTP slot isolation;
15. **M1/M2 activation-FP16 approximate lane** with quality/eval/long-greedy certification;
16. compiled-decode, B2/B4, workload-derived cache tuning and long-prefill-during-decode stress.

Turnkey persistence additionally stamps cached/session state with tokenizer/model/runtime identity and fails closed/self-heals on mismatch.

Canonical center remains **40 TG / 400 cold PP**.

## Dual-M1 DS4-0731

PP2/layer ownership remains primary; TP2 remains control; AProjQ4 remains primary candidate.

Report AProjQ4 in separate cold/full-prompt and incremental-agent PP lanes. Do not pool equal-context observations with different fresh increment sizes. Keep request-adaptive speculation, mapping/OS/command-buffer/residency diagnostics, tool-observation and exact session gates.

Canonical center remains **15 TG / 180 cold PP**.

## Single M1 Max64 Qwen3.8-27B

P69 remains separate: **P69B12 frozen/promoted; P69B13 next from existing profiling only**.

After the exact/native baseline, run activation-FP16 as a separate approximate serving A/B with quality certification. Do not mix it into P69 exactness or the 110-PP exact-runtime target.

Canonical center remains **25 TG / 110 native cold PP**.

## RTX 5070 Ti16 Qwen3.8-27B

No target change. Keep full-residency Q3_K_XL + native MTP, DFlash control, CUDA linked-runtime/driver provenance, ubatch/prompt-shape stability, draft-cache net-memory accounting, MTP-head quant and small-N verifier tests. Parallel serving inherits the per-sequence draft-context sizing rule.

Canonical center remains **120 TG / 250 cold PP**.

---

# Standing decisions strengthened this pass

- Dual-M1 Flash and DS4 remain **PP2/layer ownership first, TP2 control**.
- Ordinary no-spec recurrent rollback is a separate certification surface from MTP rollback.
- MTP/draft context must be sized and tested per sequence/slot, not only by aggregate server context.
- Cold/full PP and incremental-agent PP are separate metrics; record actual fresh tokens, increment size and cap.
- AProjQ4's measured PP effect is chunk-size dependent; its decode result remains stronger.
- M1/M2 activation-FP16 is an approximate quality-certified lane, not exact-runtime evidence.
- Known prompt horizon should pre-size QSA indexer capacity where practical.
- Recurrent checkpoint density is a first-class memory/reuse tradeoff.
- Persistent session state requires tokenizer/model/runtime identity and safe invalidation.
- Text-only DS4 tool failures must be diagnosed before compaction/context-capacity conclusions.
- Production-layout fidelity, driver/runtime provenance and verifier-width numerical invariance remain mandatory.
- Stronger/different hardware and non-bit-exact mechanisms do not move exact-machine targets by themselves.
- P69 exact verifier work remains isolated from external serving/runtime research.
