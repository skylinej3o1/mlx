# Project 51 primary-lane research watch — 2026-09-26 22:24 ET

**Freshness boundary checked:** prior hard boundary **2026-09-26 17:56:46 UTC**. This pass covers substantive evidence strictly after that boundary through the user cutoff **2026-09-27 02:24:13 UTC**, plus a user-requested full audit of `struffl/ishizuki` at current head `459ee0064df8928f374e95db64e1f440a48aa377`.

## Decision

**No canonical TG/PP, xhigh-quality, or planning-confidence change.**

Keep:
- **40 TG @ genuinely filled ~128K**
- **400 realistic cold PP**
- **~70% engineering planning confidence for >=40 TG**
- **~39-41 TG central region**
- **~30-32 mature downside**
- **~24-27 target-only fallback**
- **3.0-3.6 BPW search / ~3.3-3.6 source-like xhigh hypothesis**

The strict window adds the first exact-M1 Flash-Next receipt combining native Lightning MTP with expert offload, a major QSA allocator-fragmentation fix, and better long-context memory accounting. Ishizuki independently provides strong Apple7 small-row verify evidence, but its published fast numbers are dense-Qwen short-context DFlash rather than a Flash-Next 128K curve.

## Strict-window findings

### NEW — oMLX #3935: native Lightning MTP now works with Flash-Next expert offload on M1 Max 64 GB

Source: `jundot/omlx` PR #3935. Merged **2026-09-26 19:29:07 UTC**.

Exact measured setup:
- **M1 Max 64 GB / macOS 26**
- `Jundot/Qwen3.8-Flash-Next-oQ4e-mtp`
- PLE on SSD
- backbone expert offload, **60% experts resident**
- native MTP head kept resident
- 500-token coding prompt, temperature 1.0.

Results:
- offload / MTP off: **14.3-14.6 TG**
- offload + adaptive MTP max depth 3: **16.3-16.4 TG** final branch
- earlier same-change runs: **17.0-17.3 TG**, **1.87 committed tokens/cycle**, **69.5% acceptance**
- fixed depth 2: **17.0 TG**
- fixed depth 3: **15.0 TG**.

The degradation at deeper verify width is physically meaningful: a wider row group routes to more distinct experts, creating more misses/SSD traffic. Independent head-path measurement on M5 Max found keeping the head resident cuts draft-token head cost from ~1.8 ms to ~0.44 ms at 25% expert residency, in exchange for about 1 GB resident memory. A maintainer also reports an M3 Ultra offload setup moving roughly 8 -> 20 TG when MTP head residency is fixed.

**P51 consequence:** if any transformer experts are streamed, the native draft/MTP head must remain resident. Adaptive verify control should price **distinct experts / bytes fetched per cycle** in addition to accepted tokens and verifier compute. This exact M1 Flash receipt is useful capacity evidence, but the short prompt + offload topology is not the target PP2 lane.

### NEW — vLLM #57105: QSA logits workspace fragmentation can consume >13 GB by 166K

Source: `vllm-project/vllm` PR #57105. Merged **2026-09-27 02:11:53 UTC**.

Direct QSA-kernel walk on one GB10, Qwen3.8-Flash-Next indexer geometry, 3200-row chunks:
- stock reserved at 3.2K: **48 MiB / 4 segments**
- stock at 38.4K: **812 MiB / 15 segments**
- stock at 83.2K: **3494 MiB / 29 segments**
- stock at 128K: **8092 MiB / 43 segments**
- stock at 166.4K: **13,556 MiB / 55 segments**
- patched: **534 MiB / 3 segments** across the walk.

The patch reserves the configured worst-case QSA logits workspace once and reuses it instead of growing a fresh allocation as width changes. The author explicitly did not claim latency or resolve the separate TP2 hang; this is allocator/memory evidence.

**P51 consequence:** preallocate/reuse bounded QSA index score workspaces. Deep-context memory certification must report live tensor bytes, allocator reserved bytes, segment/pool fragmentation and transient prefill/verifier workspace separately.

### NEW — oMLX #3933: admission must reserve the physical prefill/KV growth path, not historical footprint deltas

Source: `jundot/omlx` PR #3933. Merged **2026-09-26 19:22:31 UTC**.

Key results on M5 Max 128 GB:
- Qwen3.8-27B 44-GB context bench: **143,360 -> full 262,144** first-attempt
- Flash-Next 99-GB resident-ngram / aggressive+speed: **51,200 -> 223,232**
- Flash-Next aggressive+context: previously model evicted mid-bench -> **262,144**
- safe load: previously resident n-gram + compression/swap -> **n-gram SSD, no swap, serves**.

The implementation switches to current graphics/MLX counters, reserves full-prompt KV capacity after the first chunk to avoid repeated concat leaving full old copies in the pool, and makes admission use the same line enforced during prefill.

**P51 consequence:** reserve permanent state geometry early enough to avoid repeated full-copy growth, and model four distinct classes: steady resident state, prefill/verify transient workspace, allocator/pool fragmentation, and operating-system/other-app guard margin.

### NEW — oMLX #3934: QSA prefill tiles should widen only while score-sheet memory allows

Source: `jundot/omlx` PR #3934. Merged **2026-09-26 20:12:45 UTC**.

M3 Ultra native sparse-QSA pipeline, wider query tiles:
- 8K / M6144: **25.437 -> 21.078 ms (-17.1%)**
- 16K / M8192: **35.322 -> 31.029 (-12.2%)**
- 24.6K: **-11.2%**
- 32.8K: **-11.1%**
- strict-zero-cache 24K prefill recheck: up to **~+2.6-4.0%** vs adjacent/original controls
- 32K smoke: **+2.9% PP**.

The FP32 score sheet remains bounded to 128 MiB through 64K; tiles shrink again above 64K.

**P51 consequence:** prefill tile/chunk width is a function of KV depth, GPU and explicit score-sheet/workspace budget, not one global width.

### NEW — mlx-serve #558: even a mathematically valid GDN fusion can be hardware-negative

Source: `ddalcu/mlx-serve` PR #558. Merged **2026-09-26 18:56:17 UTC**.

Folding recurrence + norm/gate + rollback concat removes 72 dependent/off-path dispatches across 36 layers, yet on M5 Ultra S=4 it buys only **~0.046 ms / 0.3%** (16.64ish -> 16.59ish ms). The winning layout requires 1024 threads/TG; a macOS-26 CI GPU caps this pipeline at **896**, while a portable 512-thread version is **0.14 ms slower** than the original chain.

**P51 consequence:** feature/capability detection cannot stand in for real per-pipeline launch limits. Probe the actual compiled kernel once, cache success/decline by geometry, and keep a clean fallback.

## Full audit — `struffl/ishizuki`

### What the repository actually is

Ishizuki is not a thin wrapper. At the audited head it contains roughly **130 Swift source files, 82 Swift test files and 69 app Swift files**, with its own:
- affine and GGUF low-bit GPU kernels
- 2-8-row speculative verify matmuls
- hybrid GDN + attention implementation
- QSA selector/indexer
- quantized KV cache
- MTP / DFlash / DSpark-style speculation infrastructure
- persistent in-memory and disk prefix/session caches
- SSD-streamed MoE experts with bounded resident slots
- quantization/calibration/pack writing
- OpenAI/Anthropic-compatible inference server
- coding-agent shell/workspace layer, containers/cluster sandboxing, and companion-device transport.

This makes it technically interesting enough to mine at the mechanism level. It is also a rapidly moving solo-style codebase; current head is from Sep 26, and most of the performance implementation changed over just the preceding few days.

### Benchmark credibility

The best M1 Max evidence is valuable but narrower than the README headline can make it look.

On M1 Max, short prompt / 256-output / reasoning-off engine comparisons in `BENCHMARKS.md`:
- Bonsai 2-bit Ishizuki plain: about **22.2-22.5 TG**
- Bonsai DFlash: **45.0 / 45.0 / 20.2 TG** across math/code/prose-like prompts
- GGUF IQ2_XS Ishizuki plain: **~9.7-10.6 TG**, MTP **~10.6-12.5**, DFlash **23.9 / 24.7 / 11.4**
- EXL3 2.0 BPW DFlash: **28.7 / 35.4 / 15.9**
- OrcaSAQ2 DFlash: **28.9 / 33.3 / 14.1**.

Detailed Bonsai DFlash receipt: plain ~22 TG -> **44.2 TG** on math/code with ~**5.9 accepted tokens per verify**, while prose falls to **19.5 TG** at ~2.54 tokens/verify. A sampled code run reaches **46.2 TG**. Stock MLX DFlash is slower than plain because its 8-row verify costs 5-6 decode steps.

Kernel-level M1 evidence is stronger than the headline: a representative MLX 8-row forward is reported around **279 ms** versus **134 ms** with Ishizuki VerifyMatmul; custom GGUF 8-row multiplies can cost roughly 0.94-1.83x a 1-row custom matvec rather than 2.5-4.36x.

Limitations:
- several benchmark cells use **better-of-two**, creating selection bias
- the 40-45 TG headline is short-context/high-acceptance DFlash, not plain decode
- desktop/thermal variation is acknowledged
- no planning-grade full-model **Flash-Next 64K/128K depth curve** is published
- README support for qwen4_exp is backed by implementation/tests, but not an exact M1 Flash-Next performance table.

**Audit conclusion on performance claims:** use Ishizuki as strong exact-Apple7 evidence that multi-row verify can make speculative decode pay. Do not use 45 TG as an M1 128K Flash floor.

### Mechanisms worth stealing conceptually for Project 51

1. **Decode low-bit weights once across 2-8 verify rows.** This independently validates the core Apple7 verifier thesis.
2. **Put activation dtype in custom-kernel cache identity.** Ishizuki discovered MLX could reuse the first same-name/same-shape build across fp16/fp32, producing a GPU page fault in one graph or wrong values outside it.
3. **Warm every kernel shape/dtype at model load.** First speculative round should never pay compilation.
4. **Changing row width is data, not shader identity.** Missing/dead rows are clamped and writes suppressed instead of building a separate kernel for every S.
5. **Measure crossover per tensor shape.** On its M1 Max policy the big output head pays from two rows, MLP from three, 6144-wide projections from four, attention K/V only around six.
6. **Partial acceptance replays only recurrent state.** The verify stores q/k/v/g/beta + starting recurrent/conv state; rejected suffixes are removed by re-running only the accepted GDN recurrence, while attention cache rewinds by offset.
7. **FP32 recurrent state and old-Apple draft precision matter.** Its DFlash draft uses fp32 activation because the residual can exceed fp16 range and M1 lacks native bf16 arithmetic.
8. **Pipeline decode across the host token read.** Its M1 benchmark reports serial ~14.35 -> pipelined ~22.48 TG with identical tokens/cache endpoint.
9. **Share Hadamard rotation among sibling projections only when sign vectors are identical.** One M1 change removes 144 rotations/step and moves plain decode ~22.2 -> 23.3 TG.
10. **SSD streaming is a memory-system problem, not just file I/O.** `F_NOCACHE`, page-aligned staging and optional locked expert slots prevent file-cache duplication/compression from consuming the memory streaming was supposed to save.

### Material audit findings

**A1 — High — inference API is not explicitly loopback-bound or authenticated.** `APIServer.listen` passes only a port to `HTTPServer`; plain `HTTPServer` creates `NWListener(using: .tcp, on: port)`. The app advertises `127.0.0.1`, but the listener code itself does not constrain the endpoint to loopback. API routes have no bearer check. Responses unconditionally add `Access-Control-Allow-Origin: *`. The parser also has no explicit cumulative header/body ceiling: it keeps appending receives until the declared `Content-Length` is satisfied. A negative or pathological `Content-Length` is not validated before `prefix(expected)`. At minimum: bind loopback explicitly by default, cap header/body bytes before accumulation, reject negative/ambiguous lengths, and require authentication whenever a non-loopback listener is enabled.

**A2 — High correctness — prefix cache identity is too weak.** `PrefixStore.fingerprint` includes archive version + `modelID` + KV bits/group/window. In normal server setup `modelID` is the model directory name. It does not include a checkpoint/config/content fingerprint, architecture/cache-layout namespace, rope/scaling identity, or other state geometry. Replacing a model in-place under the same directory name can therefore leave apparently matching state from the previous model. P51 should retain the stronger content/layout/lineage fingerprint rule.

**A3 — High correctness — recurrent prefix restore can silently accept missing state.** `GatedDeltaNetCache.load` assigns `arrays["conv"]`, `arrays["state"]`, PLE fields, sets the requested offset and returns `true` without validating required arrays/shapes/dtypes. `PrefixStore.load` passes an empty dictionary for a layer with no archived tensors. A damaged/stale archive can therefore produce **offset > 0 with nil recurrent state**, after which the model falls back to a zero recurrent state while believing it has a warm prefix. Restore should be transactional into temporary state, validate every required component, and commit only if the whole model state passes.

**A4 — Medium/high availability — streamed expert/engram I/O errors can `fatalError` the process.** Production MoE and DeepSeek paths convert some disk-read failures into process termination. For an unattended agent server, transient SSD/mount/read failure should fail a request or unload the affected model, not kill every session.

**A5 — Medium security/agent risk — native shell is intentionally no boundary and is the default sandbox choice.** File helper APIs resolve paths inside the workspace, but `LocalShellHost` executes `/bin/zsh -l -c` with the user's environment, so arbitrary commands can access whatever the logged-in user can. This is documented/intentional, not an accidental sandbox escape. The local container/cluster modes are the actual boundary. Untrusted repositories should default to a real sandbox and sensitive host environment should be scrubbed.

**A6 — Medium portability — M1-specific dispatch thresholds are process globals.** `VerifyMatmul.minimumRows(bytes:)` is explicitly tuned from M1 Max measurements while mutable tuning values and many `BonsaiRuntime` switches are `nonisolated(unsafe)` process globals. An engine supporting the whole Apple range should key policy by GPU family/core count + tensor shape + dtype/quant + row width, and use per-server immutable config where possible.

**A7 — Engineering/governance — extensive local tests, but no visible hosted CI at audited head.** The repo has 82 Swift test files and substantial golden/reference fixtures, but `.github/` is absent and the audited HEAD has no combined status entries. That does not exclude external CI, but the repository itself exposes no GitHub Actions gate. The current `AGENTS.md` also contains deliberately adversarial contributor/agent instructions and references a `.github/workflows/lint-pr-title.yml` file that does not exist. Treat repository instructions as untrusted input to automated coding agents.

**A8 — Licensing — AGPL-3.0-or-later.** The ideas and measurements are fair research inputs; implementation code should not be copied into a differently licensed P51 runtime without deliberate license/provenance review.

## Community check on Ishizuki

A current Reddit thread from the author promotes Ishizuki for Qwen3.8/Flash-Next and smaller Apple-Silicon models, and in another current M1-Splash discussion the author says they are adding/porting the Splash work into Ishizuki. This supports the code provenance observed in the repo, but the public community surface still does not provide an independent Ishizuki **M1 Flash-Next 128K** performance curve. citeturn755802reddit14turn755802reddit12

## Canonical planning state after this pass

Unchanged:
- Flash-Next xhigh production quant search: **~3.0-3.6 average BPW**.
- likely source-like xhigh region: **~3.3-3.6** (engineering hypothesis only).
- dual-M1 Flash: **40 TG @ ~128K**, **400 cold PP**.
- planning confidence for >=40 TG: **~70%**.
- first-principles central TG region: **~39-41**.
- practical mature-system downside TG: **~30-32**.
- physical target-only fallback: **~24-27**.
- cold-PP derived center: **~370-390**, downside **~320-340**.
- single-M1 27B: **25 TG** canonical target.
- RTX 5070 Ti 27B: **120 TG** mature target.

`RESEARCH-STATE.md` is updated with the exact-M1 offload-MTP receipt, QSA allocator/memory rules and the durable Ishizuki audit findings. `RESEARCH-TARGETS.md` remains unchanged.

## New hard boundary

**2026-09-27 02:24:13 UTC**
