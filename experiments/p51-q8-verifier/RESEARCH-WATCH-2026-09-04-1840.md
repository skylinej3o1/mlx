# External runtime research watch — 2026-09-04 18:40 ET

Freshness boundary for this pass:

- project branch checkpoint: `621bcd5352c1ef7430fecf3cf8f1715f1c83ac97`
- checkpoint time: **2026-09-04 19:59:18 UTC**
- classify evidence created/updated strictly after that timestamp as **FRESH**;
- older material newly recovered here is **BACKFILL** or **CORRECTION**, not fresh evidence.

This pass moves **no canonical TG/PP target or confidence row**. It materially changes agent-serving
cache policy, the DS4-agent #973 diagnosis, and RTX-5070-Ti memory/stability qualification.

---

# Canonical target calibration — unchanged

| Model / hardware | Working TG | Confidence | Working cold PP | Confidence |
|---|---:|---:|---:|---:|
| **Flash-Next — 2x M1 Max 64 / TB4** | **40 tok/s** | **~55-60%** | **400 tok/s** | **~55-60%** |
| **Qwen3.8-27B — M1 Max 64** | **25 tok/s** | **~55-60%** | **110 tok/s native/exact-runtime** | **~60%** |
| **Qwen3.8-27B — RTX 5070 Ti 16 GB** | **120 tok/s** | **~60-65%** | **250 tok/s** | **~55-60%** |
| **DS4-0731 — 2x M1 Max 64 / TB4** | **15 tok/s** | **~60-65%** | **180 tok/s** | **~60%** |

No exact dual-M1 sustained Flash TG, exact dual-M1 DS4-0731 sustained TG, or new exact 5070-Ti
speed receipt crossed the target-movement threshold.

---

# Fresh / material

## DS4 #977 — exact KV reuse survives text → image → image agent turns

PR #977 was created **2026-09-04 20:27 UTC**, after the cutoff. It unifies text-only and
image-conditioned checkpoint lookup around the longest prefix that produced identical model inputs.
Conditioning spans are validated by token location, row count and SHA-256 of the encoder output.

Apple Metal validation reported:

- append first image: **18,073 / 18,435 prompt tokens reused**;
- append second image: **18,807 / 19,079 prompt tokens reused**.

This is not a dual-M1 throughput ruler and does not move DS4 TG/PP. It is strong serving evidence
that **exact prefix/session reuse should be treated as a first-class agent execution path**, not a
best-effort optimization that disappears at modality boundaries.

Consequences:

- exact reuse remains a latency objective distinct from cold PP;
- agent qualification should include text-only → image → appended-image turns when vision is used;
- changed/moved/removed conditioning must rewind before the affected span rather than silently reuse
  incompatible state;
- the same general principle applies to Flash-Next: preserve exact reusable state across long-lived
  coding-agent sessions whenever model/runtime state permits.

## llama.cpp #28404 — Blackwell co-resident process + CUDA-graph interaction is now factorially isolated

Issue #28404 existed just before the cutoff, but the post-cutoff follow-up completes a 2×2 test on
2x RTX 5060 Ti / sm_120:

| replicas | CUDA graphs | fatal CUDA errors |
|---|---:|---:|
| single | on | 0 |
| dual co-resident | on | **2 / 2 blocks, both second replica** |
| dual co-resident | off | 0 |
| single | off | 0 |

The reporter therefore isolates the failure to **co-resident independent server processes + CUDA
graphs together**. `GGML_CUDA_DISABLE_GRAPHS=1` removed the fatal errors in that experiment; with
only two blocks the measured throughput cost was within run-to-run spread, so do not claim a graph-
off speedup or universal free workaround.

This is mechanism transfer only, not exact 5070-Ti evidence. For the user's normal single-5070-Ti,
single-server lane it does **not** justify disabling CUDA graphs by default. If a future setup uses
multiple co-resident CUDA server processes/devices, add a graph-on/off concurrency stress cell to
qualification before blaming model math or quantization.

## llama.cpp #28378 — MTP draft-KV quantization can consume *more* VRAM; fresh independent corroboration

The PR predates the cutoff, but a **2026-09-04 22:08 UTC** comment independently reports the same
counterintuitive behavior and adds that **DFlash did not show it** in that user's check.

The PR's Qwen3.8-27B / 16-GB example at 64K context shows why net memory must be measured rather
than inferred from KV element size:

- draft KV unquantized: CUDA compute buffer **126.77 MiB**, total GPU use about **15,573 MiB**;
- q8 draft K/V: CUDA compute buffer **374.03 MiB**, total GPU use about **15,711 MiB**.

So quantizing the draft cache reduced one object while increasing scheduler/compute workspace enough
for **net VRAM to worsen** in that configuration.

Do **not** transfer those absolute numbers to the exact RTX 5070 Ti unless physically reproduced.
The exact-lane consequence is nevertheless direct and important:

1. test MTP draft-KV **off vs q8** with identical target quant/context;
2. record total VRAM, compute-buffer reservation, acceptance, TG and maximum healthy context;
3. promote draft-cache quantization only if **net** usable headroom improves;
4. include a DFlash control because its draft-memory economics may differ.

This strengthens the current rule that a 16-GB configuration is promoted only by measured fully
resident headroom, never by nominal bytes-per-KV calculations.

---

# Backfill / correction

## DS4 #969 likely explains the #973 “1.9K context full” symptom more specifically

The 15:50 note correctly rejected #973 as evidence of a DS4 engine/KV context ceiling, but its
provisional label of generic tool-result compaction was too broad.

Pre-cutoff PR #969 identifies a concrete agent path:

- `ds4_chat_append_multimodal_message` required a loaded vision encoder for every tool/user append;
- on DeepSeek without `--vision`, even a **text-only tool observation** could therefore fail;
- the agent could not commit the tool result and fell into **spurious compaction ending in
  “context full after compaction”**;
- proposed fix: require vision only when images are present and use the DeepSeek-native
  `<tool_result>` wrapper.

That matches #973's shape closely: DeepSeek, no `--vision`, a file-read tool call, then compaction
and an apparent ~1.9K ceiling despite `-c 32768`.

Corrected classification:

> **agent tool-observation path first; compaction second; not model-context capacity unless a
> post-fix physical reproduction proves otherwise.**

The DS4 agent-shell gate should therefore include text-only tool results with and without a vision
encoder, large tool payloads, repeated tool calls after compaction, and continuation after summary
rebuild.

## oMLX #3439 implements the cache-block control implied by #3430/#3443

PR #3439 predates the cutoff, so this is implementation backfill rather than fresh evidence. It
adds an explicit `arrays_cache_block_size` operator setting/CLI override and deliberately keeps
cache-block granularity independent from prefill step size.

That matches our existing policy from #3443: **cache block size is workload geometry**. Small
64–256-token blocks can be right for short-turn agents even when the hardware/prefill floor is much
larger; the cost is extra recurrent-state boundary snapshots on cold long prompts.

No target movement. When physically qualifying Flash or 27B agent serving, sweep block size against
the real prompt distribution instead of copying an upstream default.

## Stable llama.cpp `v0.4.0` was published just before the prior cutoff

The 15:50 note said a stable `v0.4.0` release/tag was still absent. GitHub now shows:

- tag/release: **`v0.4.0`**;
- published: **2026-09-04 19:56:47 UTC**;
- target commit: **`427291b5b34cd914a31b3fd3b61a68f6184f4b9f`**.

That publication was ~2.5 minutes **before** the 19:59:18 cutoff, so classify this as a
**search-lag correction**, not fresh post-cutoff evidence.

The release explicitly says Qwen3.8-Flash-Next support is initial and optimization work remains
pending. Therefore:

- use `v0.4.0` / its exact tagged commit as the first reproducible community baseline candidate;
- do not confuse release stabilization with a throughput promotion;
- experimental sparse-QSA, PLE residency/direct-read, compiled-decode and later fixes still need
  separate physical A/Bs on the M1 pair.

---

# Exact-rig no-change confirmations

- **Dual-M1 Flash-Next:** no new exact sustained TG or completed long-context exact follow-up
  surfaced. Existing 2x M1 Max64/TB4 evidence remains topology/correctness, not a rate receipt.
- **Dual-M1 DS4-0731:** no new sustained generated-token denominator surfaced. #922 remains the
  exact ~34K distributed prefill anchor, not a TG result.
- **RTX 5070 Ti 27B:** `aipruner/qwen3.8-3bit-test-in-16GB-GPU` still has
  `pushed_at=2026-08-20T19:16:50Z`; no new exact-card receipt.
- **Apple 27B:** `ARahim3/mlx-dspark` still has `pushed_at=2026-09-01T10:54:45Z`;
  Layr's Qwen3.8 challenge remains `pushed_at=2026-08-29T07:05:19Z`.

---

# Current consequences by lane

## Dual-M1 Flash-Next

Qualification order:

1. pin/certify **llama.cpp `v0.4.0` / exact tagged commit** on both Macs;
2. plain exact **PP2/layer-owned** baseline; TP2 control;
3. PLE residency/page-cache/direct-read policy A/B;
4. sparse-QSA wide-prefill A/B;
5. pooled QSA-prefix retention / rollback correctness;
6. recurrent rollback + **singleton MTP** A/B;
7. adversarial parallel-MTP slot-isolation gate before MTP concurrency >1;
8. compiled-decode B2/B4 end-to-end A/B;
9. workload-derived cache block size + exact prefix/session reuse;
10. SSD expert streaming only as secondary capacity/control lane;
11. combine passing mechanisms, then multi-agent long-prefill-during-decode stress.

Canonical center remains **40 TG / 400 cold PP**.

## Dual-M1 DS4-0731

Keep **PP2/layer ownership primary, TP2 control** and AProjQ4 as primary serving candidate with
AProjQ8 control.

Agent qualification now explicitly separates:

- engine context capacity;
- text-tool observation correctness without `--vision`;
- compaction/summary reconstruction;
- exact prefix reuse across ordinary and, when relevant, multimodal turns.

Canonical center remains **15 TG / 180 cold PP**.

## Single M1 Max64 Qwen3.8-27B

Canonical center remains **25 TG / 110 native cold PP**. Cache block size remains workload-selected;
ANE-assisted PP remains a separate approximate lane with hidden-bank admission accounting.

P69 remains unchanged: **P69B12 frozen/promoted; P69B13 next from existing profiling only**.

## RTX 5070 Ti16 Qwen3.8-27B

Qualification order becomes:

1. CUDA build/link/runtime provenance preflight;
2. ubatch 256/512 + neutral/code/tool prompt-shape stability matrix;
3. fully resident Q3_K_XL + native MTP speed lane;
4. **MTP draft-cache memory A/B: unquantized vs q8; measure net VRAM/workspace/max context**;
5. DFlash draft-memory/speed control;
6. small-N Blackwell verify A/B;
7. BF16/Q6_K/Q4_K-imatrix MTP-head A/B;
8. GSQ-RCO context/quality lane;
9. only if multiple co-resident CUDA server processes are used: CUDA-graphs on/off stress.

Canonical center remains **120 TG / 250 PP**.

---

# Standing decisions after this pass

- No performance target moved.
- **PP2/layer ownership remains primary** for dual-M1 Flash and DS4; TP2 remains control.
- Stable llama.cpp `v0.4.0` is now available as the reproducible baseline candidate, but its own
  release notes say Flash optimization is incomplete.
- Prefix/session reuse is a first-class agent latency objective and must remain numerically/correctly
  conditioned; it is not cold PP.
- Cache granularity follows the real prompt distribution, not RAM size.
- DS4 #973 should be debugged through the tool-observation path before treating compaction as the
  primary fault.
- On 16-GB NVIDIA, **nominally smaller draft KV can consume more total VRAM**; only net residency and
  maximum healthy context count.
- CUDA graphs stay enabled by default for the ordinary single-5070 lane unless exact evidence says
  otherwise; co-resident multi-process serving gets its own graph-stability gate.
- Stronger/different hardware mechanisms update the test plan unless exact physical evidence earns a
  target move.
