# Project 51 primary-lane research watch — 2026-09-30 01:37 ET

**Freshness boundary entering this pass:** **2026-09-29 23:52:05 UTC**.  
**User cutoff:** **2026-09-30 05:37:52 UTC**.

## Decision

**Durable STATE + TARGETS update; no TG/PP/AA-center movement.**

The main changes are architectural/correctness:

1. Qwen3.8-Flash-Next's **compressed normalized QSA index-key store** may enter an FP8 experimental lane after BF16 control, while structural QSA state remains exact.
2. Any S>1 speculative sparse working set must be resolved as the **union across the whole verification window before mutation/eviction**.
3. Long-context B2/B4 throughput is now an explicit qualification gate; short-context batching gains do not imply long-context aggregate gains.
4. Exact static/root prefix state must be domain-separated from ordinary partial-prefix matching and use bounded tail-generation retention.

The P51 maximum-context target remains:

> **DASLab GSQ-RCO IQ3_XXS, 3.00 transformer bpw + genuine 262,144 context on RTX 5070 Ti 16 GB + 64 GB host, with Flash-aware compressed/streamed KV.**

Conditional physical-fit prior remains **~85%**. No 262K TG/PP center is assigned.

## NEW — SGLang stores Qwen3.8 compressed QSA index keys in FP8 with xhigh quality parity

Commit:
`eb9c9ee99d47bf4c526a06cd84da59cd9cf4e2a5`  
PR #39614  
Timestamp: **2026-09-30 05:11:46 UTC**.

The new `--qsa-indexer-dtype fp8_e4m3` path changes only:
- normalized compressed QSA index-key storage;
- the matching index query used by the scoring GEMM.

It does **not** quantize:
- main full-attention K/V;
- the raw pending key ring;
- group mean / norm / RoPE computation;
- logits (still accumulated in FP32);
- structural block/page/indexer metadata.

The pending ring remains BF16.

### Real Qwen3.8 quality result

Qwen3.8-Flash-Next-FP8, B300, no speculation.  
AIME/GPQA use thinking + xhigh.

| Metric | BF16 indexer | FP8 indexer |
|---|---:|---:|
| GSM8K greedy | **97.80** | **97.65** |
| AIME26 pass@1 | **98.33** | **99.17** |
| GPQA-D pass@1 | **92.11** | **91.98** |
| GPQA majority@8 | **93.18** | **92.93** |

Kernel tests compare BF16 against eager bit-comparable behavior and FP8 against the eager chain within one e4m3 ULP; TileLang scoring uses FP32 accumulation.

This is strong evidence that **normalized compressed index-key rows** do not need the same exact-storage rule as indexer control/lineage state.

### Approximate memory effect

For the compressed QSA geometry used by the Qwen4/Qwen3.8 path:
- 1 index KV head;
- head dim 128;
- compression ratio 4;
- 12 QSA/full-attention layers.

SGLang's accounting gives:
- BF16 compressed keys: **~768 B/token**;
- FP8: **~384 B/token**.

At 262,144 tokens:
- saving ≈ **96 MiB**.

Useful safety margin, but not enough to replace full-KV compression as the main 64-GB fit lever.

Important limitation:
- SGLang currently admits FP8 indexer scoring only on **SM90/SM100**.
- The user's RTX 5070 Ti is **SM120**, so this is mechanism/quality evidence only until a Blackwell path is qualified.

## NEW — SGLang fuses QSA selected-block metadata and final KV preparation

Commits:
- `b660100c008bc15f6e6979ddbaaed5a1c037350b` — **04:52:28 UTC**
- `88f95f4b87c52044139aadcb1b2797f7e46845b9` — **04:54:34 UTC**

The Qwen3.8/Qwen-next path now:
- carries compressed block identities farther through decode/verify;
- shares graph-stable QSA metadata across draft steps;
- fuses block expansion, new-K/V placement, selected-K/V packing and validity counting near the attention boundary.

P51 rule:
- keep the QSA representation in its compact logical/block form as long as possible;
- expand/gather only at the final consumer boundary;
- do not rebuild logical->physical state independently per verifier row.

No target-number movement.

## NEW — vLLM fixes speculative sparse residency with a per-request union

Commit:
`2798f668608155bc8a8c74cb97e3ddd0d3053085`  
PR #59235  
Timestamp: **03:01:45 UTC**.

Old behavior:
- each MTP verification row resolved selected sparse pages independently;
- hot-cache ownership/LRU was shared per request;
- rows could claim the same free slot or evict a page another verification row still referenced.

New behavior:
- one block handles each request;
- form one union of every verification row's selected host pages;
- perform one LRU walk;
- load each shared host page once;
- map every row onto the stable result.

Correctness:
- the race test fails **30/30** on main's old kernel;
- passes on H100/H200/B200;
- a shrunk GLM-5.3 setup matches main tokens and drafts exactly under FULL CUDA graphs.

H100 MTP3 residency time per layer, steady:
- 1 req: **155 -> 64 us**
- 8 reqs: **185 -> 87 us**
- 32 reqs: **264 -> 167 us**
- 64 reqs: **373 -> 268 us**

P51 rule:

> **Any sparse mutable state selected by S>1 verification must reserve/resolve the union of all rows before mutation or eviction.**

Apply this to:
- selected KV/QSA pages;
- hot expert residency if verifier rows share an expert arena;
- any page/slot ownership state that can be mutated during verification.

## NEW — vLLM makes durable host backing a hard sparse-cache admission condition

Commit:
`90e13fc757cffc11b55689d9cc33d844d9606516`  
Timestamp: **04:13:29 UTC**.

HiSparse no longer creates GPU-resident pages with null/missing host backing.

Now:
- every computed page needs a host block;
- insufficient host pool defers/refuses allocation;
- startup requires enough host blocks for a max-length request plus null/COW state;
- in-flight spill ownership prevents premature reuse.

P51 rule:
- a GPU page is not truly evictable until its durable host/disk backing has already been reserved/owned;
- future hoped-for backing does not count as capacity.

## NEW — oMLX persists split-GDN exact static prefixes correctly

Commit:
`cb15799150fc6738f9c497bf5fc4569c40a666d1`  
Timestamp: **05:28:01 UTC**.

SpecPrefill static/system/tool prefixes can now persist terminal recurrent GDN state through an SSD sidecar.

Critical detail:
- exact split-GDN blocks get a dedicated domain key;
- intermediate structural placeholder blocks are not exposed to ordinary partial-prefix matching.

P51 root consequence:
- a persistent canonical system/tool root that includes exact terminal recurrent/QSA state must be **domain-separated from generic token-prefix blocks**;
- equality of token text/hash alone is insufficient to make a recurrent-state checkpoint reusable as a generic partial prefix.

## NEW — oMLX stops hybrid recurrent tail snapshots from accumulating forever

Commit:
`a28e5a87be49e8e5f8d5e91773e513ea32f05750`  
Timestamp: **05:23:49 UTC**.

Previously tail lineage pruning ran only for rotating-cache layouts. GDN/QSA/other hybrid recurrent models therefore accumulated one full-state tail per turn.

Now:
- keep the previous turn's tail as edited-turn fallback;
- drop the tail from two turns back;
- remove its GDN sidecar too.

P51 rule:
- persistent roots/private suffixes need an explicit **tail-generation retention policy**;
- “retain every valid resumable state” is a resident-memory leak at agent timescales.

## NEW/UPDATE — Strata unified snapshot core reaches ~120K soak

PR #189, based on Strata 0.1.27.

Current snapshot image includes:
- used main K/V;
- draft K/V;
- GDN/PLE;
- QSA/indexer state including spare/dead state;
- retained checkpoints;
- explicit K8V4 representation.

Admission:
- byte/slot bounds;
- physical-RAM headroom checks on Linux/Windows;
- invalid snapshot rejected before application;
- transfer/synchronization failure is fatal rather than partial continuation.

Linux RTX 4090 / IQ3_S validation:
- 1,298 real-GPU snapshot checks;
- INT8 streamed/ring and INT8/K8V4 batched-prefill gates;
- 30 return cycles at **2,026 / 39,985 / 119,987-token** prompt depths;
- known-answer + exact output/main-state parity;
- stable retained payload;
- HTTP reuse/eviction/disconnect/recovery tests.

A Sep-30 default-off regression also checks 72 requests across untouched upstream/candidate/disk builds, including a **43,170-token** INT8 ring/spec-4 prompt.

This materially strengthens P51's canonical persistent-root architecture.

Not claimed:
- exact user's hardware;
- throughput speedup;
- indefinite soak;
- HIP;
- multi-GPU whole-conversation parking.

## NEW — exact RTX 5070 Ti Strata cancellation/recovery validation

Issue #183 / PR #194.

Validation system:
- **RTX 5070 Ti 16 GB**
- Ubuntu 24.04
- CUDA 13.2
- **IQ3_XXS native pack**
- INT8 streamed K/V
- `--kv-resident 32768`
- MTP spec4.

Fixture:
- 34,719-token prompt;
- cancel after ~3 seconds;
- retry same prompt;
- then short request.

Strata 0.1.27 bug:
- cancellation leaves `err="cancelled"`;
- next long prompt sees stale error;
- engine exits and reloads.

Two-line fix:
- clears request error at request start;
- retry resumes at the **16,384-token checkpoint**;
- produces the same 64 token IDs as a fresh read;
- next request also succeeds.

Useful exact-card evidence for:
- streamed-KV state;
- checkpoint validity;
- cancellation rollback/recovery.

Not a 262K filled-context receipt.

## SAME-DAY CURRENT — genuinely deep Strata IQ3_S execution at 204K prompt depth

Original issue #183 reporter:
- RTX A4500 20 GB;
- 377 GB host RAM;
- Strata 0.1.27;
- IQ3_S;
- native 262,144 context;
- INT8 K/V streaming;
- 32,768 resident cells.

Cancelled request:
- **204,456 prompt tokens actually processed**;
- engine log: **71,966 ms = ~2,841 PP**;
- six checkpoints present before cancellation.

This is strong proof that Strata's hybrid GDN/QSA/KV-streaming state machine genuinely executes 200K+ contexts with an IQ3-class model.

It does **not** answer the 64-GB host-fit question because the machine has 377 GB RAM.

## RECOVERED CURRENT — exact 5070 Ti native-window allocation with IQ3_XXS + Q4 KV

External reported setup:
- RTX 5070 Ti 16 GB;
- llama.cpp/Unsloth;
- Qwen3.8-Flash-Next UD-IQ3_XXS;
- **262,144 configured context**;
- Q4_0 K/V;
- CPU MoE / 49 layers offloaded.

Reported:
- **20.44 TG**
- **129.29 PP**
- prompt length only **2,409 tokens**.

Classification:
- useful exact-GPU native-window allocation/startup receipt;
- **not** filled-262K throughput;
- **not** 262K resident continuation;
- not transferable to Strata performance.

## NEW — M1 Ultra two-way decode collapses at longer context

oMLX issue #4110  
Created **2026-09-30 04:22:32 UTC**.

Hardware:
- M1 Ultra 128 GB;
- Qwen3.8-27B oQ4e;
- TQ8 K/V;
- MTP heads preserved;
- 128K policy cap.

At ~20K active context, MTP off:
- B1: **21.7 TG**
- B2: **5.4 / 5.8 TG**, ~**11.2 aggregate**

Turning decode fairness off gives ~5.57 / 5.57, so the collapse is not a scheduler fairness artifact.

At ~9K:
- two-way MTP-on ~**19.4 aggregate**.

At very short context:
- B2 MTP-off ~**28.9 aggregate**, above ~20.1 solo.

Reporter's byte/rate estimate:
- B1 ~18.0 GB/step, 46 ms, ~390 GB/s;
- B2 ~19.9 GB/step, 180 ms, ~110 GB/s.

P51 consequence:
- do not infer B2/B4 scaling from shared weights or short-context batching;
- require explicit B1/B2/B4 measurements at **16K / 32K / 64K / ~128K** before multi-agent promotion;
- record kernel path and effective memory bandwidth.

This is M1 Ultra + dense27B, not dual-M1 Flash, so the existing Flash aggregate probability ladder is retained rather than numerically downgraded.

## NEW — two DGX Sparks show healthy parallelism can scale aggregate TG

TensorFold issue #123  
Created **01:32:52 UTC**.

Flash-Next TP2 on two DGX Sparks:

| Users | Existing | Parallel change |
|---:|---:|---:|
| 1 | 111 | 110 |
| 2 | 91 | 111 |
| 4 | 92 | 148 |
| 8 | 91 | 188 |

Reported replies match draft-off byte-for-byte for the tested long prompts, disconnects and multi-turn chats.

This is useful positive mechanism evidence that concurrency can work well when the batch/distributed kernels are healthy, but it does not negate the Apple long-context negative.

## NEW — mlx-serve multirow HC optimization changes real arithmetic

Commit:
`933566c4107f34d459652cd24ca0fd0f4bbf68c6`  
Timestamp: **00:50:34 UTC**.

For direct HC reads at 2-8 rows with 8-bit up weights:
- about **1.00 ms/step saved at 4 streams**;
- rare mixed elements differ by several BF16 ULPs;
- stacked one-row equality is restored for 4-bit HC weights or with `MLX_SERVE_HC_UV=0`.

P51 rule:
- a multirow performance path that changes arithmetic does not qualify for source-equivalence merely because it is close numerically;
- run near-tie/token-trajectory tests or disable it in AA certification.

## NEW — restored-prefix admission must credit state already owned

mlx-serve issue #528 / PR #621 provides a useful admission counterexample.

M5 Pro 48 GB, Qwen3.8-27B:
- 78,156 / 78,475 prompt tokens persisted;
- scheduler still billed the whole prompt at **4,790 MB** and refused with only 3,572 MB available;
- a 128,083-token prompt with **121,833 tokens restored** was refused by just **93 MB** because restored rows were billed again.

P51 rule:
- once restored state already occupies cache slots owned by the incoming request, admission must credit that ownership;
- do not bill a restored prefix as if it needs a second fresh allocation.

## NEW — TensorFold CUDA admission illustrates temporary staging cannot be double-counted as resident

Issue #112 follow-up on RTX 5090 32 GB / Qwen3.8-27B + DFlash2.

A branch correcting startup-memory accounting now serves where main reports zero fitting tokens:
- budget 26.90 GiB;
- startup estimate 23.44 GiB;
- 16,384 context admitted;
- observed peak ~18.98 GiB.

Main had effectively counted startup staging alongside resident allocations and refused everything.

P51 rule:
- distinguish resident allocations, sequential staging, and peak-overlap lifetime;
- capacity planning should reserve true simultaneous peak, not sum buffers that provably cannot coexist.

## Strict-window negative scan

From **2026-09-29 23:52:05 -> 2026-09-30 05:37:52 UTC**:

- **Strata:** no 0.1.28/0.1.29 release commit found.
- **Exact 5070 Ti / 64-GB host:** no genuinely filled 262K IQ3_XXS Strata run.
- **TurboQuant-MLX / TBQ research forks:** no new strict-window commit.
- **TensorFold:** no new main commit; issue evidence only.
- **MoEspresso:** no new exact-M1-Max ~27-TG fork/settings/context receipt.
- **DASLab:** no new official source-paired IQ3_XXS/IQ3_S 262K semantic-quality result.
- **Dual M1 Max/TB4:** no new sustained filled-128K physical receipt.

## Durable target effects

No change:
- dual-M1 Flash: **40 TG @ genuine ~128K / 400 PP / ~70% >=40 TG**
- single-M1 dense27B: **25 TG / ~110 PP**
- Strata IQ3_XXS @128K: **78 TG / ~85%**
- IQ3_XXS PP: **1,650 / 1,550 / 1,500**
- IQ3_S PP: **1,550 / 1,550 / 1,350**
- IQ3_XXS AA>=38: **~85%**
- IQ3_XXS AA>=40: **~65%**
- IQ3_S AA>=40: **~80%**
- IQ3_XXS + 262K compressed-KV conditional physical-fit prior: **~85%**
- K6/V4 long-horizon-quality prior: **~60-70%**

Added gates:
- FP8 compressed-QSA-key lane after BF16 control; structural QSA state stays exact;
- union residency for all S>1 sparse mutable state;
- B1/B2/B4 context ladder through ~128K;
- exact-root domain separation;
- bounded recurrent/QSA tail generations;
- restored-state admission credit;
- durable backing before eviction credit.

## New hard boundary

**2026-09-30 05:37:52 UTC**
