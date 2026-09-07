# External runtime research watch — 2026-09-07 17:53 ET

Starting freshness boundary: `9211221b8d998ff8cfbf67882db4e61c22596d6b` / **2026-09-07 19:24:38 UTC**.

Classification: **small but material MTP-provenance / experiment-order update; no target movement.**

`RESEARCH-TARGETS.md` is intentionally unchanged. No fresh sustained exact-target receipt surfaced for dual-M1 Flash, dual-M1 DS4-0731, single-M1 Qwen3.8-27B, RTX 5070 Ti Qwen3.8-27B or RTX 5070 Ti Tiel Coder.

---

## FRESH / material

### rMLX #540 / `abfd59e590982f8e2b0a24de31af7e7b4d008f70` — the MTP block a run *actually executes* is benchmark provenance

Post-boundary commit timestamp: **2026-09-07 20:42:40 UTC**.

The rMLX MTP round loop had been narrowing an explicitly requested speculative block to the sidecar's declared `block_size`. Every shipped Qwen3.5-family MTP sidecar in that project declares block 3, so an operator could request block 4+ and still actually run block 3.

The important correction is conceptual as well as mechanical:

- the checkpoint declaration is a **trained/default depth**, not necessarily the structural ceiling for a recursively chained MTP head;
- an explicit deeper request may be structurally valid up to the single-verify-forward ceiling;
- deeper is **not assumed faster or better** — acceptance and whole-round economics must be measured;
- an absent request keeps the conservative served default / checkpoint-aware rule, so this is not permission to silently deepen production MTP;
- every speculative loop now reports the **widest block actually executed**, rather than letting the harness infer it from the requested flag;
- the equivalence harness now refuses a labeled cell whose actual executed block does not match the cell being judged.

The project found this was load-bearing: a nominal deeper-block test could remain green even after reinstating the old clamp, because the harness was reading back its own requested value rather than the round loop's resolved value.

Their deeper recurrent-sidecar gate also demonstrates why depth is an experimental dimension rather than a correctness proxy: the deeper arm can remain within the project's greedy-equivalence tolerance while producing different whole-answer continuations on near ties. That does **not** transfer a speed or quality claim to our models; it strengthens the need to certify and label each actual depth independently.

### Promotion for Flash / Qwen27 MTP work

**Actual resolved speculative block/depth is mandatory benchmark provenance. Requested depth alone is not evidence.**

For every MTP depth cell record at least:

1. requested block/depth;
2. checkpoint-declared/trained depth;
3. actual widest block executed by the round loop;
4. per-position acceptance and accepted tokens/round;
5. partial/full-accept round census;
6. draft / verify / rollback-or-refold / whole-round timing under a charged/materialized profiler;
7. TG and wall time against the same no-spec verifier;
8. greedy-equivalence / frontier-state correctness result;
9. verifier and sidecar identity / quantization mode.

A run is **mislabelled and rejected** if the engine-reported executed block does not match the benchmark cell.

### Experiment-order consequence

After the ordinary replay semantic baseline is frozen:

1. certify the shipped/default MTP depth first;
2. measure its whole-round economics;
3. only then sweep explicitly deeper blocks as separate cells;
4. keep the deeper arm only if correctness holds and net TG/wall improves;
5. run tape/refold as an orthogonal rollback optimization, not as a way to hide depth economics.

Do not infer a hard structural cap from a checkpoint's trained depth. Do not infer a profitable depth from structural admissibility.

---

## BACKFILL / pre-boundary but useful

These merged before the 19:24:38 UTC boundary and are recorded as **BACKFILL**, not fresh evidence.

### vLLM #54890 / `94e26dd3dd7d6363b524c96521c78feb501bdc61` — FP8 QSA indexer cache

Merged **2026-09-07 12:15:45 UTC**.

Flash-Next QSA gained an FP8 E4M3 indexer-cache path with dedicated fused/unfused reference coverage and explicit tolerance around low-precision intermediate rounding.

This is useful **mechanism evidence**, not Apple-rate evidence. The portable lesson is that the QSA/indexer side cache is a separately quantizable state surface and can be evaluated independently from the main attention KV/state path.

Promotion after exact QSA set/tie/order correctness is frozen:

- test a low-bit QSA/indexer side-cache lane separately from main KV precision;
- record memory footprint and route actually selected;
- require selected-set/tie-boundary and frontier-logit equivalence under the chosen precision policy;
- do not mix a low-bit cache gain into the exact baseline before the QSA determinism oracle passes.

### vLLM #52771 / `4a806d08ee94b35356dd749bf814ee91ee93f8d0` — MTP/EAGLE offload hits could be zeroed by wrong group ownership

Merged **2026-09-07 12:16:05 UTC**.

The OffloadingConnector's speculative path had two important ownership/geometry problems for shared-group MTP models:

- when no KV-cache group self-identified as an EAGLE/drafter group, fallback behavior could treat the wrong population as speculative;
- lookup widening and the mandatory volatile-tail drop could then consume the only matched chunk and collapse a valid reusable boundary to zero;
- while a request is still drafting, the volatile trailing speculative block must remain excluded, but after request finish that exclusion must be lifted so the now-stable tail can be published.

This is external-cache/offload evidence rather than direct Apple prefix-cache evidence, but the state rule transfers cleanly.

### Promotion for our persistent-cache / SSD-host lane

Speculative cache publication and lookup must carry **group ownership + lifecycle phase**:

- target/recurrent/attention/draft groups are explicitly identified;
- volatile speculative tails are not published while rejection can still rewrite them;
- stable tail state is published once the request is finished;
- lookup widening/drop arithmetic cannot erase the only valid reusable boundary;
- a cache/offload benchmark records actual restored tokens, transferred bytes and warm wall time, not merely successful stores.

---

# Exact-rig no-change confirmation

Searches after the new 19:24:38 UTC boundary did **not** surface a new exact sustained receipt for:

- Flash-Next on 2x M1 Max 64 GB / TB4;
- DS4-0731 on 2x M1 Max 64 GB / TB4;
- Qwen3.8-27B on one M1 Max 64 GB;
- Qwen3.8-27B on one RTX 5070 Ti 16 GB;
- Tiel Coder 35B-A3B Q4/Q5 partial expert offload on one RTX 5070 Ti 16 GB + 64 GB host RAM.

Therefore the canonical planning centers remain:

| Lane | TG | Cold PP |
|---|---:|---:|
| Flash-Next — 2x M1 Max64/TB4 | **40** | **400** |
| Qwen3.8-27B — M1 Max64 | **25** | **110** |
| Qwen3.8-27B — RTX5070Ti16 | **120** | **250** |
| DS4-0731 — 2x M1 Max64/TB4 | **15** | **180** |

These remain **planning targets, not measurements**.

---

# Incremental Flash bring-up change from this pass

Keep the 15:10 certification order, with these additions/refinements:

- after exact QSA tie/set/order certification, a **separate low-bit QSA/indexer-cache A/B** may enter the optimization queue;
- persistent external/SSD cache qualification includes explicit speculative-group ownership and finish-time stable-tail publication;
- after replay correctness is frozen and the default MTP depth is certified, add an **actual-resolved-depth sweep** before promoting deeper MTP;
- every depth row is rejected if requested/labeled depth differs from the engine-reported block actually executed;
- tape/refold remains after replay correctness and is evaluated at the same resolved depth as its replay control.

Safe-serving rule is unchanged: **profitable singleton MTP + plain concurrent work** until per-slot recurrent/spec state, physical capacity, PP+MTP ownership and concurrent-state isolation are certified.

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only.**

---

# Standing decisions strengthened

- The benchmark cell is defined by what the engine **actually executed**, not what the CLI requested.
- Checkpoint-declared MTP depth is training/default provenance, not automatically a structural or performance optimum.
- Deeper speculative depth is an explicit A/B dimension with correctness and whole-round economics, not a free tuning knob.
- QSA/indexer cache precision is a separate state surface and may be optimized only after its deterministic semantic oracle is frozen.
- Speculative cache/offload state carries explicit group ownership and lifecycle; volatile tails become reusable only after they are stable.
- Cross-runtime and other-hardware results remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
