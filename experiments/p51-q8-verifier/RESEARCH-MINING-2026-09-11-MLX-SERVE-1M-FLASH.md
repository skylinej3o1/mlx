# Source-specific mining — mlx-serve Qwen3.8-Flash-Next 1M-context release

Date: **2026-09-11 ET**  
Classification: **SOURCE-SPECIFIC UPDATE / TRANSFER / MECHANISM**  
This is **not** a complete external-search pass and therefore **does not advance the hard source-freshness boundary**.

Primary sources:

- Reddit release thread: https://www.reddit.com/r/LocalLLaMA/comments/1wb7p70/qwen38flashnext_on_mlxserve_1m_context_is_released/
- mlx-serve: https://github.com/ddalcu/mlx-serve
- mixed 4/8-bit model card: https://huggingface.co/ddalcu/Qwen3.8-Flash-Next-MLX-Serve-mixed-4-8bit

---

## Executive takeaway

This is one of the strongest external validations so far of the **system architecture**, not an exact dual-M1 receipt.

The release combines:

- Qwen3.8-Flash-Next / `qwen4_exp`;
- sparse QSA beyond 2K;
- native MTP;
- mixed precision that spends low precision primarily on the giant routed-expert bulk while retaining much higher precision on control/state-sensitive paths;
- SSD/page-cache-backed n-gram/PLE lookup rather than making the 51B table resident;
- prefix caching and recurrent/SSM checkpoint retention;
- real sampled deep-context use instead of only tiny-context greedy microbenchmarks.

That direction overlaps strongly with the planned dual-M1 Flash runtime and the future **Blazer** quant/runtime co-design.

**No canonical TG or PP target moves from this note.** The headline Flash target remains **40 tok/s sustained TG at ~128K active context** plus **400 tok/s realistic cold PP** on **2x M1 Max 64 GB / TB4**.

---

## USER/DEVELOPER RECEIPT / TRANSFER — M5 Max 128 GB at extreme context

The release author reports, on **M5 Max 128 GB**, 8-bit KV and one-concurrency serving:

- approximately **40 tok/s prose at ~1M context**;
- approximately **75 tok/s coding at ~1M context**;
- temperature **1.0**, explicitly framed as deep-context real work rather than short-context repetitive greedy generation;
- roughly **117 GB peak memory** at full 1M, requiring a high wired-memory limit.

The same thread reports a context sweep approximately shaped as:

- **100+ tok/s** through ~16K;
- **80+ tok/s** through ~256K;
- about **60 tok/s** around 500K;
- about **40 tok/s** around 1M;
- prefill roughly **1700–1800 tok/s** early, staying near **1000 tok/s** toward 1M.

These are **stronger-Apple user/developer receipts**, not exact M1-Max/TB4 measurements. Do not numerically transfer them to the dual-M1 cell.

### Planning implication

The evidence materially strengthens the proposition that Flash-Next's long-context architecture can remain interactive far beyond 128K when the sparse-attention, n-gram lookup, KV/state and MTP paths are implemented well.

It therefore supports retaining **40 @ ~128K** as a defensible mature-system objective. It does **not** justify raising the exact M1 target yet because the M5 lane has:

- newer GPU/tensor hardware;
- one coherent memory system;
- no TB4 pipeline boundary;
- different quantization;
- different runtime and kernel implementations.

---

## MEASURED / MODEL-CARD FACT — mixed 4/8-bit pack is a coarse Blazer analogue

The published model card says the pack is about **75 GB resident** before KV and uses the following precision layout:

| Tensor family | Stored precision |
|---|---|
| routed experts — 512 experts x 48 layers, ~121B parameters | **4-bit, group 64** |
| attention | **8-bit, group 64** |
| GDN | **8-bit, group 64** |
| hyper-connections | **8-bit, group 64** |
| sparse-attention indexer | **8-bit, group 64** |
| shared experts | **8-bit, group 64** |
| LM head | **8-bit, group 64** |
| token embedding | **4-bit, group 64** |
| n-gram table | **4-bit, group 32** |
| routers, inject gates, norms, convs, SSM state | **BF16** |
| MTP head | same policy as trunk |

This is not our target quant and should not be called Q5/Q6-equivalent. But architecturally it is a powerful demonstration of the strategy:

> **compress the enormous bandwidth-dominant expert bulk aggressively while preserving substantially higher precision on small but behaviorally/control-sensitive paths.**

### Blazer consequence

Do **not** constrain the eventual ~5.x-BPW search to “mostly Q5 with selected Q6/Q8.” Add a first-class family:

> **Q4-ish routed experts + Q6/Q8/BF16 control/state tensors**, tuned to an overall effective ~5.x-BPW-class operating point.

Candidate search axes should include:

1. routed-expert precision separately from trunk/control precision;
2. QSA indexer precision separately from attention K/V and projection precision;
3. GDN recurrent/state-sensitive projections separately from generic MoE bulk;
4. shared experts separately from routed experts;
5. MTP-head sensitivity separately from target-trunk sensitivity;
6. packing/group size chosen for **M1 kernel geometry**, not merely nominal BPW;
7. difficult-tail behavioral robustness, MTP acceptance, task wall-clock and tokens-to-solution in addition to PPL/KL/TG.

This is a **candidate-family expansion**, not evidence that generic Q4 experts are automatically quality-safe on M1.

---

## MEASURED / MODEL-CARD FACT — 51B n-gram table is a sparse lookup plane, not resident model bulk

The model card describes the 51B-parameter n-gram table as:

- one merged **4-bit** `ngram_table.bin` of about **32.0 GB**;
- intentionally outside normal MLX safetensor loading;
- memory mapped;
- per token, only **16 rows** are fetched/dequantized on CPU;
- only the resulting **2560-wide vector** is uploaded;
- the full table is never made resident by the runtime;
- the OS page cache provides the natural caching layer.

The card contrasts this with ordinary MLX-style packing that would make the quantized table resident and add roughly 32 GB to active memory.

### Dual-M1 consequence

Treat PLE/n-gram as a **separate sparse lookup plane** with policy choices rather than a fixed model-residency assumption:

1. SSD/page-cache backed;
2. fully resident when memory allows;
3. hot-subset resident / cold SSD;
4. stage-local ownership under PP2;
5. explicit prefetch/coalescing where profiling justifies it.

Certification must record:

- PLE residency policy;
- cold/warm page-cache condition;
- SSD traffic and page faults;
- per-stage ownership/duplication;
- effect on PP and TG;
- 128K and 200K+ memory headroom.

The earlier oMLX thread evidence that resident PLE can be faster on roomy 128-GB systems and this mlx-serve SSD/page-cache design are **not contradictory**: the correct policy is hardware/memory-pressure dependent.

---

## MEASURED / MODEL-CARD FACT — QSA keeps the actual attention payload bounded

The model card states that after 2048 tokens each attention layer reads only the **512 most relevant 4-token blocks per query**, plus the query's partial block, selected by a small indexer.

This reinforces the existing architecture split:

- dense-prefix-length growth should not translate directly into dense K/V attention work;
- long-context degradation therefore points increasingly toward selection/indexing, gathered K/V mechanics, recurrent/state handling, MTP verification, memory pressure and cache policy;
- selected-K/V sparse paths must qualify B1 decode **and** actual MTP verify/narrow-window shapes.

This aligns with the fresh oMLX #3553 evidence that the measured value of gathered/narrow long-context optimizations increases with context.

---

## USER/DEVELOPER RECEIPT — MTP is strongly workload-shaped

The model card's older M4 Max receipt reports serial decode around 60 tok/s and MTP around 78 tok/s, with approximately:

- **+41% on code**;
- **a few percent negative on prose**;
- approximately **-4% on an 8.5K prompt** in that earlier configuration.

The 1M Reddit release likewise reports a large prose-vs-code split (~40 vs ~75 tok/s at extreme context).

### Promotion

The headline system cannot certify MTP using one content family. Keep at least:

- code/editing/agent loops;
- ordinary English prose;
- multilingual/CJK;
- tool-call-heavy workloads;
- deliberately low-acceptance / novel-content controls.

Measure:

- plain TG;
- MTP TG;
- tokens/cycle and acceptance by position;
- task wall-clock;
- tokens-to-solution;
- output/agent correctness.

A high coding-agent TG is valuable for the user's actual workload, but it must not silently redefine the generic 40 @ ~128K target cell.

---

## SYSTEM DESIGN implication — cache and recurrent state are part of the product, not benchmark decoration

The release's one-concurrency 1M example uses:

- `--prefix-cache-mem 10GB`;
- `--prefix-cache-entries 1`;
- `--ssm-checkpoint-max 16`;
- 8-bit KV;
- native MTP.

This strongly reinforces the planned local-agent architecture:

> **stable repo brain/prefix -> cached -> selectively append task-local context -> retain recurrent checkpoints -> avoid repeatedly ingesting giant cold contexts.**

For the dual-M1 system, ~128K is therefore both:

- a real **sustained-performance target cell**, and
- a **capacity/robustness level**, not the amount of context every normal coding-agent request should cold-ingest.

Persistent repo graph/summaries remain a complementary system optimization rather than a substitute for long-context capability.

---

## Important caveats / non-promotions

Do **not** promote any of the following as exact dual-M1 facts:

- 40 tok/s at 1M on M5 -> 40+ on M1;
- 75 tok/s coding at 1M -> expected generic TG on M1;
- 1700–1800 PP on M5 -> a direct PP multiplier for M1;
- 4-bit routed experts -> proven Q5/Q6-equivalent quality;
- 117 GB M5 peak -> direct PP2 memory accounting.

The Reddit author's later statement that a future release may improve ~1M generation by ~50% is **forward-looking developer commentary**, not measured current evidence and should not enter target calibration until a reproducible release/receipt exists.

---

## Consequences for the current project

### Dual-M1 Flash-Next

Keep:

- **40 tok/s @ ~128K active context** headline TG objective;
- **400 tok/s** realistic cold PP objective;
- PP2/layer ownership primary; TP2 control;
- QSA gathered selected-K/V and recurrent/state locality as top long-context levers;
- PLE/n-gram policy as an explicit residency/SSD/hybrid/stage-local decision;
- singleton profitable MTP serving until concurrent-state isolation is physically certified.

Add to the eventual qualification matrix:

1. mixed-precision expert-vs-control variants;
2. PLE resident vs SSD/page-cache vs hybrid vs stage-local;
3. Q8/BF16 KV initially, with lossy KV only after quality/correctness gates;
4. code/prose/CJK/tool-call/low-acceptance long-context cells;
5. prefix-cache + recurrent-checkpoint warm-session tests distinct from cold PP;
6. memory headroom at ~128K and 200K+ under the actual PP2 ownership layout.

### Future Blazer

Expand the candidate family from one narrow “mostly Q5” hypothesis to at least:

- **A — Q5-dominant:** bulk Q5, sensitive Q6/Q8/BF16, insensitive Q4 where proven;
- **B — expert-aggressive:** routed experts Q4-ish, control/state/shared/QSA/MTP tensors Q6/Q8/BF16, tuned to similar effective BPW;
- **C — sensitivity-optimized mixed 5.x:** tensor/layer-specific Q4/Q5/Q6/Q8 assignments from the calibration corpus.

Compare at the **same effective memory/bandwidth envelope** where possible. The winner is determined by task success + difficult-tail robustness + acceptance + task wall-clock + TG/PP + memory/context, not by nominal bit label.

### P69 / Qwen3.8-27B

No impact. **P69B12 remains frozen/promoted. P69B13 remains next from existing measured high-leverage GDN/projection/downstream-tail structure. Do not reopen P69B8, P69B9 or P69B10-C.**

---

## Standing decision

This mining note **strengthens the architecture/quantization thesis** and broadens the Blazer candidate search, but it does **not** move any canonical performance target and does **not** advance the hard external-search cutoff.
