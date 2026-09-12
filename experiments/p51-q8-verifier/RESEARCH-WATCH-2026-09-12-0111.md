# External Runtime Research Watch — 2026-09-12 01:11 ET

## Scope / freshness

This complete pass screened substantive source activity strictly after the previous hard boundary `2026-09-12 00:22:42 UTC` through the request timestamp `2026-09-12 05:11:02 UTC`.

Primary lanes searched:

- Qwen3.8-Flash-Next — 2x M1 Max 64 GB / TB4;
- Qwen3.8-27B — one M1 Max 64 GB;
- Qwen3.8-27B — RTX 5070 Ti 16 GB + host RAM;
- DeepSeek-V4-Flash-0731 / DS4 — 2x M1 Max 64 GB / TB4;
- portable oMLX / vLLM / llama.cpp mechanisms relevant to those lanes.

Repositories and community surfaces screened included `jundot/omlx`, `vllm-project/vllm`, `ggml-org/llama.cpp`, `antirez/ds4`, Reddit and Hugging Face. Rediscovery/crawl time was not treated as evidence time.

**Result:** no fresh exact measured receipt was found for the dual-M1 Flash lane, M1 Max64 27B lane, canonical RTX5070Ti16 target setup, or dual-M1 DS4-0731 lane. Canonical TG/PP targets therefore remain unchanged. P69 is untouched.

---

# Fresh new evidence

## vLLM #56550 — consumer-Blackwell NVFP4 KV execution geometry

**Classification: FRESH NEW / BLACKWELL MECHANISM TRANSFER. Not an exact RTX5070Ti16 speed receipt.**

PR #56550 was created at `2026-09-12T02:06:13Z`, within this pass, and was still open at head `e22ffd10692274571c4765e394f4a4f96c0e055e` during screening.

The patch enables NVFP4 KV cache on SM120 consumer Blackwell through FlashInfer and makes several pieces of physical execution identity agree:

- HND KV-cache layout resolution on sm12x;
- linear / unswizzled V block-scale writes;
- an explicit `nvfp4` KV-dtype gate in the FlashInfer backend;
- attention block-size / layout plumbing;
- removal of an SWA primary-block-size choice that violated the NVFP4 + SWA block-geometry constraint on SM120.

Validation was on **RTX 5090, Qwen3.8-27B-QUASAR-NVFP4, TP=2, DFlash**. The report says the engine started, KV was actually allocated as NVFP4, CUDA graphs captured, and end-to-end chat produced correct output. It explicitly says the evidence is from a combined SM120 NVFP4 stack. There is no portable standalone TG/PP speed receipt here.

### Durable promotion

For the RTX 5070 Ti / Blackwell lane, `KV precision` is not a sufficient execution identifier. Record and verify together:

1. requested KV dtype;
2. physically allocated KV dtype;
3. attention backend;
4. KV layout / axis order;
5. scale representation and write order;
6. primary-attention and SWA block sizes;
7. block-size divisibility / kernel geometry constraints;
8. graph-capture route;
9. executed route under the measured cell.

The existing provenance ladder therefore applies to KV format itself:

`requested -> configured -> backend-admitted -> physically allocated/layout-resolved -> graph-captured -> executed`.

This is directly useful for 5070 Ti bring-up because a nominal low-bit KV setting can be configured while the physical backend/layout/geometry combination is unsupported or different. It does **not** move the current 120 TG / 250 cold-PP planning targets.

---

# Screened but not promoted as fresh target evidence

## vLLM #56177 — shared device-side NVFP4 expert pool

The PR resurfaced after the boundary because its branch was rebased/committed at `2026-09-12T03:47Z`; the performance body is older evidence rather than a newly timestamped receipt, so it is **not reclassified as fresh**.

The older measurements remain interesting transfer evidence: a shared GPU expert bank plus device-side LRU/planning keeps routing/copies inside CUDA graphs and reported a large improvement over UVA expert offload on a constrained NVIDIA Flash-Next setup. The mechanism is compatible with the standing rule that sparse arrival/residency machinery must not move ownership/state decisions onto an uncontrolled host path. No canonical target is changed from this rediscovery.

## vLLM #56509 — later DeepSeek V4.1 SM120 geometry

The PR body predates this pass. Its after-boundary activity did not add measured hardware validation; the stated fix changes SWA/indexer block size to satisfy later V4.1 / SM120 kernel geometry. Retain only as a geometry-provenance reminder. It is not DS4-0731 evidence.

## vLLM #56323 — DSv4 DFlash JIT/warmup migration

Post-boundary activity was CI/rebase churn rather than a new benchmark/result. No promotion.

## oMLX

Fresh post-boundary activity was dominated by UI/i18n work. No new exact Flash-Next M1 or 27B M1 performance receipt was found. Older distributed Qwen4Exp TP work and the previous YaRN/expert-offload findings remain in their existing classifications; they are not made fresh by fork pushes or rediscovery.

## llama.cpp

Commits through the request cutoff contained no newly surfaced Metal/Qwen target-lane result in the screened set. OpenCL/WebGPU changes were not promoted. A commit timestamped after `05:11:02 UTC` is outside this pass by construction.

## antirez/ds4

No commits or issues updated after the previous boundary were found. The DS4-0731 target lane therefore remains unchanged.

## Community / Hugging Face / Reddit

Search resurfaced useful RTX5070Ti16 Qwen3.8-27B measurements and model pages, but their underlying measurement/post timestamps were older or not proven to be after `2026-09-12 00:22:42 UTC`. They remain retained older evidence only. Crawl time is not evidence time.

---

# Consequences by active lane

## RTX5070Ti16 Qwen3.8-27B

No target move. Add KV execution identity to the certification sheet: dtype, physical allocation, layout, scale ordering, backend, SWA/main block geometry and actual captured/executed route must agree. A CLI flag alone is not proof.

## Dual-M1 Flash-Next

No target move. PP2/layer ownership remains primary and TP2 remains control. Existing QSA workspace, speculative semantic-axis, draft-stage ownership, expert-tail, PLE and long-context requirements remain unchanged.

## M1 Max64 Qwen3.8-27B / P69

No target move. `P69B12` remains frozen/promoted. `P69B13` remains next only from existing measured high-leverage GDN/projection/downstream-tail profiling. Do not reopen P69B8, P69B9 or P69B10-C.

## DS4-0731 dual M1

No target move. Later DeepSeek V4.1 GPU geometry remains transfer-only unless exact DS4 topology/runtime evidence appears.

---

# Canonical targets — unchanged

| Model / hardware | Working TG | Working cold PP |
|---|---:|---:|
| Flash-Next — 2x M1 Max64 / TB4 | 40 tok/s @ ~128K active context | 400 tok/s |
| Qwen3.8-27B — M1 Max64 | 25 tok/s | 110 tok/s native/exact-runtime |
| Qwen3.8-27B — RTX5070Ti16 | 120 tok/s | 250 tok/s |
| DS4-0731 — 2x M1 Max64 / TB4 | 15 tok/s | 180 tok/s |

The Flash 40 @ ~128K figure remains a planning objective, not an exact measured dual-M1 receipt.

---

# New hard freshness boundary

**`2026-09-12 05:11:02 UTC`**

For the next complete search, only substantive source activity strictly after that timestamp is fresh. Repository rebases, crawler timestamps and search rediscovery do not refresh older measurements.