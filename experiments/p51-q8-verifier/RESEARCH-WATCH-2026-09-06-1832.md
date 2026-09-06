# External runtime research watch — 2026-09-06 18:32 ET

Starting branch checkpoint: `d40aeef2c2a966ee2c2e238b2b9ec9b8d6d4683d`

Starting hard freshness cutoff: **2026-09-06 16:58:15 UTC**.

## Executive result

This pass is **material for baseline semantic correctness, hybrid cache/state restoration, multi-agent capacity certification and session-state validation, but does not move any canonical TG/PP target**.

No fresh sustained receipt surfaced on the exact 2x M1 Max 64 GB / TB4 Flash topology, the exact 2x M1 Max DS4-0731 topology, the exact M1 Max 64 GB Qwen3.8-27B serving lane, the exact single RTX 5070 Ti Qwen3.8-27B lane, or RTX 5070 Ti Tiel Coder.

The highest-value changes are:

1. **BACKFILL:** llama.cpp merged a semantic correction to Gated DeltaNet normalization just before the previous pass cutoff; the historical stable pin should now be treated as a control, not automatically as the production semantic baseline;
2. fresh vLLM hybrid-cache work shows a prefix hit can seed recurrent state in the **wrong block-size units**, causing either an illegal read or — more dangerously — a silent restore from another valid state row;
3. llama.cpp #28495 now has a controlled root cause: the large warm-slot PP collapse is carried by unified KV on CUDA/HIP because those FA paths skip tail mask blocks but not all-`-INF` interior blocks; **Metal already has interior skipping**, so keep this as an Apple regression oracle but downgrade the probability of the same exact root cause on Metal;
4. fresh ds4 DSpark work reinforces the persistent-state trust boundary: verified target rows may extend the rolling support window, while temporary draft rows stay outside persistent history; measured gfx1151 gains are transfer evidence only;
5. ds4 added complete frontier-vector validation and demonstrated a case where **every recorded argmax stayed identical while the full vectors drifted**;
6. ds4 fixed an in-memory session serialization bug where `fmemopen` could overwrite the final payload byte, making byte-for-byte memory-vs-file snapshot identity a first-class session gate;
7. fresh vLLM Qwen3.8-27B concurrency data shows a sharp aggregate-throughput cliff when the shared recurrent/KV block pool cannot actually back the configured active state columns, even though `max_num_seqs` permits them;
8. fresh vLLM compressed-KV data shows a capacity win can carry a strongly context-length-dependent decode cost, reinforcing context-slope qualification rather than one short-context throughput number;
9. adaptive speculative policy should be calibrated only after kernel warmup/capture, not during cold kernel warmup.

`RESEARCH-TARGETS.md` remains untouched.

---

# BACKFILL / material

## llama.cpp PR #28068 / merge `5fdfa6282936576d2f352d4b97f397a109f207a6` — GDN normalization semantics corrected

Merged **2026-09-06 16:46:22 UTC**, about twelve minutes before the previous pass final cutoff. The 12:45 watch did not record it, so this is a **BACKFILL**, not fresh evidence.

The correction changes Gated DeltaNet q/k normalization from the old llama.cpp form:

`x / max(sqrt(sum(x^2)), eps)`

to the reference form:

`x * rsqrt(sum(x^2) + eps)`.

The PR cites Qwen FlashQLA, corrected Transformers behavior and the FLA-backed vLLM/SGLang implementations as using the latter form. The change affects architectures including `qwen35`, `qwen35moe`, `qwen3next` and **`qwen4exp`**.

The PR also reports model-level numerical comparisons for Qwen3.8-Flash-Next and Qwen3.8-27B. These rows are numerical-divergence evidence, not a throughput receipt and not sufficient by themselves to infer an end-task quality delta.

### Promotion

This is not an optional speed optimization. It changes the model math.

For the Flash appliance baseline:

- retain the previous pinned llama.cpp revision only as a historical/compatibility control;
- establish a semantic candidate baseline that contains the corrected GDN normalization, preferably by an isolated patch/cherry-pick first so the normalization change can be separated from unrelated newer runtime changes;
- compare reference logits/state at multiple GDN frontiers before performance tuning;
- stamp the GDN normalization implementation/version into baseline provenance;
- do not compare pre-fix and post-fix TG/PP as if they were exactly the same inference implementation.

No target changes until the corrected path is measured on the exact target hardware.

---

# FRESH / material

## vLLM #55600 / PR #55601 — prefix-cache hits can index recurrent state in the wrong block units

Issue created **2026-09-06 17:53:29 UTC**; fix PR opened **18:05:47 UTC**.

The failure comes from using a global/cache `block_size` to seed a recurrent-state index after the engine has reduced that global size to the minimum across heterogeneous prefix-cacheable groups.

In the reported hybrid configuration:

- recurrent / mamba block size: **7,168** tokens;
- speculative/drafter attention group: **64 or 1,024** token blocks;
- the recurrent state block table is indexed in recurrent-block units;
- the buggy seed divides cached tokens by the smaller global block size.

Consequences:

- if the resulting column exceeds the recurrent-state table width: illegal memory read / Xid 31;
- if the resulting column remains in range: the request can silently restore an **unrelated recurrent state block**;
- with multiple sequences, a wrong column may land in another request's valid row, turning a crash into silent cross-slot semantic corruption.

The proposed fix divides by `mamba_block_size`, the unit actually used by the recurrent state table.

Manual reported validation after the one-line fix includes:

- 57,344-token / eight-block cached prefix: crash before, successful warm completion after;
- 13-, 34- and 63-block prefix hits completing;
- warm multi-needle recall matching cold at 100K / 250K / 450K;
- 100K warm TTFT **8.7 s** vs **139 s** cold in the reported stack;
- a three-hour soak with **133/133** requests completing, contexts up to 184K and no Xid/memory drift.

These measurements are GLM/vLLM/DGX-Spark evidence and are not Flash M1 performance rulers.

### Promotion

Cache geometry must be typed by semantic state, not represented by one generic block-size integer.

Add to Flash certification:

- attention/prefix block size;
- recurrent-state checkpoint/block size;
- draft/MTP block size;
- QSA/indexer geometry;
- slot/state-row ownership;
- every restore index expressed and asserted in its native unit.

Adversarial restore cells should deliberately use unequal state/cache/draft geometries. Test single-slot and multi-slot separately so an out-of-range failure cannot hide a wrong-but-valid cross-row restore.

---

## llama.cpp #28495 UPDATE — warm PP collapse is specifically unified-KV interior-mask work on CUDA/HIP

The 12:45 note recorded the symptom but root cause was still open. Fresh controlled A/B now localizes it.

On the reported HIP path, `--kv-unified` makes a sequence's flash-attention work cover stale/released interior cells in the shared pool because CUDA/HIP only skip the tail using `KV_max`; they do not skip all-`-INF` blocks in the interior.

Controlled matched-prompt A/B:

- split/per-sequence cache: roughly **-3.1%** drift across repeats;
- unified KV: roughly **-41.8%**;
- a short 512-token predecessor did not materially hurt the following long prefill;
- a ~100K predecessor did, showing the cost tracks shared-pool high-water/stale-cell extent rather than simply "request number 2".

Upstream `llama-batched-bench` reproduction in the issue reports the same shape: unified-KV S_PP falling materially across B=1/2/4 while split-cache behavior stays much flatter.

Crucially for the target appliance, the issue traces the missing optimization specifically to CUDA/HIP and notes that **Metal already skips interior masked blocks**.

### Promotion / downgrade

- Keep the warm-slot matrix in the Apple certification suite.
- Downgrade the hypothesis that the exact #28495 root cause should reproduce on Metal.
- Add a direct Metal assertion/profiler cell proving released/other-slot interior blocks are actually skipped under the chosen server/distributed path.
- If the custom PP2 path changes mask construction or slot ownership, re-prove the optimization instead of assuming native Metal behavior survives the distributed wrapper.
- Keep request-1 versus request-2+ PP in serving reports because other warm-state regressions remain possible.

No Apple PP target movement.

---

## ds4 `394865c5d14d93f0d2b792cab15ce6ed07e6be29` — persistent rolling support must contain trusted target rows, not temporary drafts

Fresh **2026-09-06 20:26:09 UTC** ROCm/DSpark work changes target-feature alignment and support-window retention.

Key state rule:

- verified/trusted target captures merge into persistent rolling support history;
- temporary speculative draft rows remain outside that persistent history;
- target features are paired to their actual positions;
- capture gaps reset safely rather than letting stale draft state become authoritative.

The same gfx1151 change reports sampled coding continuation moving from roughly **14.17/14.38 to 25.10/24.46 tok/s at 8K/16K**, 24/24 long-coding checks, 7/7 sampled-coding checks, a tool round trip passing, and a 64K native continuation at 22.61 tok/s.

These rates are **direct gfx1151 ds4 measurements**, not Apple transfer rates and not target-table evidence.

### Promotion

For Flash MTP/session state:

- persistent state changes only on verifier-committed/target-authoritative rows;
- draft rows have explicit temporary ownership/lifetime;
- rollback removes all uncommitted draft contributions;
- rolling-window boundaries are checked by absolute token position, not only physical ring index;
- capture gaps and session restore re-establish the logical window before any new draft is admitted.

This directly strengthens the planned pre-verify snapshot / commit / replay oracle.

---

## ds4 `85a4f0e6115a3cf38dfdb3f9531edde57ecf6574` — full-vector frontier gates catch drift that argmax misses

Fresh **2026-09-06 20:37:42 UTC** testing work adds strict validation of complete score tables and complete float32 frontier vectors.

It rejects missing/duplicate rows, malformed/non-finite values and denominator/coverage inconsistencies, and compares every expected frontier vector rather than only top-N/argmax summaries.

A documented measured comparison retained the **same argmax ID at all four recorded frontiers while the full vectors still differed**, including a large maximum absolute logit difference in that artifact.

### Promotion

For exact-runtime mechanism promotion:

- argmax identity is necessary but not sufficient;
- record full-vector hashes at selected frontiers where storage cost is reasonable;
- for recurrent/QSA state candidates, also fingerprint state tensors or compact canonical projections;
- separate `bit-identical`, `numerically-drifted but behaviorally passing`, and `invalid artifact` outcomes;
- preserve prompt/model/build/quant/runtime provenance outside the vector dump itself.

This is especially important for optimizations where coherent greedy text can mask state drift for many tokens.

---

## ds4 `c0a6119f363ef82125877142f13fb3fe491cba14` — in-memory session serialization can corrupt a byte independently of model logic

Fresh **2026-09-06 21:59:05 UTC** fix.

`fmemopen` appends a NUL terminator even in binary mode. When the backing allocation exactly matched serialized payload length, closing the memory stream could overwrite the final byte of the final cache tensor.

The fix allocates one extra byte for the stream terminator without changing the serialized payload length and adds memory-snapshot versus file-serialization byte comparisons, including grow/reuse cases.

### Promotion

Session certification must distinguish model-state correctness from serialization-transport correctness.

Add:

- canonical serialized length;
- byte hash of file snapshot;
- byte hash of in-memory snapshot;
- exact file-vs-memory payload identity;
- save/load/save round-trip identity where the format contract allows it;
- final-byte and boundary-byte sentinels in model-free tests;
- semantic logits/state equivalence after restore in model tests.

A correct recurrent-state algorithm is not sufficient if the snapshot carrier mutates bytes.

---

## vLLM #55580 UPDATE — configured slots are not the same as physically backed recurrent-state concurrency

Fresh update/comment on Qwen3.8-27B hybrid GDN, FP8 KV, TP2, 2x RTX 5060 Ti.

The reported workload shows a sharp c32 aggregate-throughput step as the profiled shared state/KV pool crosses roughly 190K tokens / about 120 unified blocks:

- below the threshold: roughly **229–233 aggregate tok/s**;
- above: roughly **300–303 aggregate tok/s**;
- c8 stays around 161 and single-stream around 29 across the arms.

A fresh production comment attributes the shape to recurrent/GDN state columns sharing block-ID capacity with KV, with draft slots adding further pressure. The comment reports a much larger block-ID requirement than a KV-only sizing intuition in that stack; treat that factor as stack-specific user evidence, not a universal constant.

The more durable lesson is the sharp threshold: scheduler configuration may claim N sequences while physical recurrent-state pool capacity can back fewer useful simultaneous state columns.

### Promotion

For the mild-concurrency appliance claim, record at startup and per test:

- configured slot/sequence count;
- physically allocated recurrent state rows/columns;
- attention/cache blocks;
- speculative draft reserve;
- context length per slot;
- actual admitted/scheduled active sequences per step;
- aggregate TG and TTFT at concurrency 1/2/3/4;
- restart-to-restart allocator/capacity variance.

A B2/B4 result is not interpretable without proving the runtime really has enough state capacity to execute B2/B4 rather than time-slicing or silently constraining active rows.

This is CUDA/vLLM transfer evidence, not an Apple rate ruler.

---

## vLLM #55610 — compressed KV can gain capacity while losing long-context decode throughput

Fresh **2026-09-06 21:41 UTC** report on Qwen3.8-27B hybrid, TP2, 2x RTX 3090, no speculative decoding.

Reported TurboQuant k8v4 versus FP8:

- KV token pool: **+37.3%**;
- decode at ~3.2K prompt: **-2.8%**;
- decode at ~55.3K prompt: **-31.1%**.

The reporter interprets the slope as consistent with per-position compressed-KV read/dequant work but explicitly does not claim a proven kernel diagnosis.

### Promotion

Any cache/state compression candidate must be profiled as a **context-length curve**, not a single short-context cell:

- short / medium / long / ~128K;
- TG, PP, TTFT, memory and concurrency capacity;
- whole-agent wall time;
- exact quality/state gate.

Memory savings that increase nominal context/concurrency may still lose useful work per hour at the context lengths the appliance is meant to serve.

---

## vLLM `6865e67f0be02d53694517f6f71d7fb96492792d` — adaptive speculative policy must not calibrate on cold kernel warmup

Fresh **2026-09-06 18:31:40 UTC** fix temporarily disables the adaptive-verification manager during fixed kernel warmup, then restores it for later capture/calibration and serving.

### Promotion

If/when Flash uses adaptive draft depth or route-selection cost models:

- compile/kernel warmup first;
- calibrate after warmup on the execution path intended for serving;
- version/persist calibration with runtime/model/hardware identity;
- keep cold-start cost metrics separate from steady-state policy calibration;
- do not let first-use compilation costs teach the adaptive controller that otherwise-profitable draft widths are expensive.

This does not change the current safe plan of fixed/correctness-gated MTP first.

---

# Focused follow-up status

- **oMLX #3462:** no post-cutoff comments; real-agent cache-capture efficacy remains active.
- **oMLX #3464:** no post-cutoff comments; explicit generated-token/TG provenance remains active.
- **llama.cpp #25187:** no post-cutoff comments; full-head MTP quant before aggressive FR-Spec remains active.
- **llama.cpp #28425:** no post-cutoff comments; ordinary no-spec recurrent rollback remains active.
- **llama.cpp #28433:** no post-cutoff comments; per-slot draft-context sizing remains active.
- **llama.cpp #28448:** no post-cutoff comments; allocator identity remains monitored.
- **llama.cpp #28495:** materially updated; root cause now localized to unified-KV interior-mask handling on CUDA/HIP; Metal already has the cited interior-skip capability.
- **MLX #4409:** no new exact target result surfaced.
- **Tiel Coder:** no fresh exact RTX 5070 Ti result.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash:** no fresh sustained exact 2x M1 Max64/TB4 TG or new exact-topology cold-PP receipt.
- **Dual-M1 DS4-0731:** no fresh sustained current-head generated-token denominator on 2x M1 Max64/TB4.
- **M1 Max64 Qwen3.8-27B:** no fresh exact single-M1-Max target-model TG/PP receipt.
- **RTX 5070 Ti Qwen3.8-27B:** no fresh exact single-card target-lane TG/PP receipt.
- **RTX 5070 Ti Tiel Coder:** no fresh exact-card receipt.

Therefore **no canonical target or confidence row moves**.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Keep PP2/layer ownership primary and TP2 as control.

The important baseline change is that corrected GDN normalization is now a semantic prerequisite. Recommended order:

1. preserve the historical pinned llama.cpp revision as a control;
2. create a minimally changed candidate containing the corrected GDN normalization and certify reference frontier logits/state;
3. exact PP2/layer-owned baseline on both Macs; TP2 control;
4. ordinary no-spec recurrent rollback / growing-session correctness;
5. typed cache/state grid identities and mixed-grid restore oracle;
6. cache-layout/handler round-trip + model/tokenizer/runtime/GDN-normalization identity;
7. cold-first request + request/step epoch ownership for async/external PLE/state;
8. QSA block/cell selected-set, tie-membership and order oracle;
9. batch-composition invariance at concurrency 1/2/3/4, identical + mixed prompts, no-MTP first;
10. real-agent cache capture with canonical recurrent/attention reusable boundary;
11. immediate async-store race + forced eviction/pause progress;
12. warm-slot PP request 1 vs request 2+ and explicit Metal interior-mask-skip proof;
13. realistic-depth QSA/attention vs MoE/GDN/host profiler;
14. QSA known-horizon reservation + capacity/footprint accounting;
15. PLE residency/page-cache/direct-read;
16. small-N versus wide-N kernel-route matrix;
17. MTP reconcile using ordinary prefill chunk geometry;
18. MTP pre-verify snapshot / commit / replay with temporary draft rows excluded from persistent history;
19. per-slot draft context + actual recurrent-state capacity at parallel 1/2/3/4;
20. production sampler-law certification for temperature/top-p/top-k, RNG and rollback positions;
21. full-vector frontier/state fingerprints on mechanism candidates;
22. session file/memory byte-identity + semantic restore equivalence;
23. concurrent pure-prefill isolation;
24. adversarial parallel-MTP slot isolation;
25. M1/M2 activation-FP16 approximate lane only after exact freeze;
26. compiled B2/B4; combine passing mechanisms; long prefill while other sessions decode.

Safe serving remains profitable singleton MTP + plain concurrent work until the multi-slot state, batch-composition and capacity gates pass.

## RTX 5070 Ti Qwen3.8-27B / Tiel Coder

No target movement. Preserve the known Qwen resident baseline. Test Tiel Q4/Q5 partial expert offload using the 64 GB host RAM rather than defaulting to 3-bit.

Add from this pass:

- include corrected GDN semantics in any llama.cpp Qwen comparator;
- treat cache-compression performance as a context-length curve;
- record physically backed recurrent-state capacity if hybrid serving uses multiple slots;
- retain realized backend/residency placement and whole-agent wall time.

## Single M1 Max64 Qwen3.8-27B

P69 remains isolated: **P69B12 frozen/promoted; P69B13 next from existing profiling only**.

The GDN normalization merge changes external serving-runtime semantics but does not retroactively reopen the frozen verifier campaign. If the new normalization is tested in the verifier repo, do it as a new explicit experiment/control rather than silently changing P69B12.

## Dual-M1 DS4-0731

No exact-rig target update. Fresh ds4 changes are strong state/certification mechanism evidence, but the measured rates in this pass are gfx1151/ROCm and must not be transferred to M1 Max.

---

# Standing decisions strengthened this pass

- Correct GDN math is part of baseline identity, not an optimization knob.
- Historical runtime pins remain useful controls even when semantic corrections require a new candidate baseline.
- Cache/state block sizes are typed semantic units; one generic block-size value cannot safely index heterogeneous recurrent/attention/draft grids.
- Multi-slot restore must catch wrong-but-valid cross-row state reads, not only crashes/out-of-range accesses.
- Persistent speculative history contains verifier-authoritative target state, not temporary draft rows.
- Full-vector frontier identity catches drift that argmax equality can miss.
- Session serialization must be byte-faithful independently of model-state logic.
- Warm unified-KV PP collapse #28495 is now a CUDA/HIP-specific mechanism; Metal retains a regression gate but not the same prior suspicion level.
- Configured concurrency is not physical recurrent-state capacity; measure actual active state columns and scheduled occupancy.
- Cache compression is qualified over context length, not a short-context headline.
- Adaptive speculation calibration belongs after kernel warmup.
- Cross-runtime / other-hardware gains remain mechanism evidence until exact target-hardware reproduction.
- No target movement without exact target-topology evidence or exceptional explicit justification.
- P69 remains isolated.