# Project 51 — Strict Research Watch — October 28, 2026 10:12 EDT

**Strict window:** AFTER 2026-10-28T13:28:02Z THROUGH 2026-10-28T14:12:42Z (09:28:02–10:12:42 EDT).
**New hard freshness boundary:** 2026-10-28T14:12:42Z.
**Scope:** source ISTA-DASLab Qwen3.8-Flash-Next GSQ-RCO IQ3_S, PLE and MTP precision, two independent M1 Max32GPU/64GB native Metal KVarN/Relay and owner RTX5070Ti16/Core Ultra7 265F 64GB Linux; actual occupied128/262K, persistent xhigh agents and reliability. Only new-window event timestamps qualify. No owner experiment performed, no approvals granted.

## 1. New Basalt IQ3S memory optimization and reliability PRs: OPEN, not main

### Basalt #114 — elastic KV RAM homes

[Source PR #114](https://github.com/jesdga95/basalt/pull/114), created **13:48:00Z**. Previously pinned RAM copies of experts in the long elastic KV tail are discarded until a deep request actually needs them. At request admission, copy-less experts take temporary host RAM homes, released upon cache regrowth. The prior layout can be restored with --exp kv_tail_copies=1. Under --parallel the old copies remain in use; **no multiagent batch improvement inferred**.

**Physical non-owner** RTX5080 16GB @360W, Intel Core Ultra9 285K, 62GB DDR5; ORIGINAL GSQ-RCO IQ3_S, 262K configured, actual measured 40K/85K/131K, developmental baseline **without earlier main 8d94e805**. MemAvailable ready **7376→9218MiB (+1842)**, after actual131K **6070→7319MiB (+1249)**; pinned expert copies **47.57→45.31GiB**, retained lent slot copies4975→4093. Temporary homes at 131K ~932MiB. Controlled 131K teacher-forced decode **+0.16% CI[-0.26,+0.58]** (4 pairs), pooled **−0.01% CI[-0.46,+0.43]** (8 pairs), no significant decode change. 40K neutral. At 40K prompt read **−0.71% CI[-1.30,-0.11]**, at 131K **~−0.6%** due to admission device-to-host copies. Greedy output equal in stable tests; MTP acceptance unchanged.

**Important caveats:** does **not** establish recovery of last watch's ~−2.67% deep decode loss caused by main 8d94e805 (#108): exact main+PR114 deep139K paired test missing. On low initial RAM a one-run 15K request took ~5.4GiB new RAM homes instead of reading ~6GB files, but 15K prefill became 3.37→4.12s; a 40K follow-up 7.44→7.23s, not controlled A/B. Actual site was RTX5080/285K, not user 5070Ti/265F, nor M1. No small-fixed-chunk deep run, --parallel, cross-agent cache correctness or worst RAM-pressure with held homes yet. One source A/B's divergent token after a changing VRAM-placement session was also observed in unchanged baseline self-runs; do not attribute without fixed allocation oracle.

**Proposed owner test:** identical original IQ3S weight and runtime SHAs, main vs PR with rollback toggle, 4K/40K/131K/262K actual occupancy, first/late TG, cold/warm PP, headroom, pinned pages, DMA, IOPS, file fault and MTP acceptance; deterministic source-token/logit and tool-action equality. New idea promising for memory fit, **not measured throughput win**.

### Basalt #113 — RAM guard shed/wait without killing an active coding turn

[Open PR #113](https://github.com/jesdga95/basalt/pull/113), created **13:47:57Z**. Below the existing MemAvailable guard, release parked conversation/cache and free heap, admit new requests after bounded 30s wait, terminate active decode only on CRITICAL under hard 1GiB or pronounced Linux memory-pressure stalls; if pressure source absent, retain conservative stop. A live thinking-answer continuation of <=256 prompt tokens bypasses wait to prevent 30s final-answer stall. Cancellation can stop waiting tasks; server retains critical protection.

Non-owner physical RTX5080/285K/62GB original IQ3S supervised memory-hog test: 61K-token prompt/2500 requested output while another process dipped available RAM below **3161MiB guard**. Main stopped after **339 generated tokens**. PR delivered **2500 tokens in 26.5s**, shedding one parked session (~226MiB) and heap (~70MiB); another pending request waited8.1s then generated200 tokens, canceled request exited at2.04s. Previous development variant introduced erroneous 30s continuation stall (57.1s), corrected to27.2s in follow-up test. Greedy identity on small and 40K prompts and CPU tests. Tradeoff: dropped parked session will need re-prefill; pressure fallback differs by OS. **Not owner hardware or general 128/262K 5-agent verification.** PROPOSED fail-safe acceptance test, no automated RAM-hog permitted now.

### Basalt #111/#112 — same-bit expert kernel improvements, local only

[PR #111](https://github.com/jesdga95/basalt/pull/111), created **13:42:31Z**, AVX512/BMI2 sign mask via PDEP and IQ3_S/IQ2_S grid gather; IQ3_S 200-row single-thread kernel times **73.9→71.4µs 1 token, 82.5→73.7 2 tokens, 91.8→83.0 4 tokens** (−3%,−11%,−10%), bitwise test hashes; CPU host time reduced~0.15ms/window but overall RTX5090 Laptop175W+Ryzen9955HX3D IQ3XXS decode within variation.

[PR #112](https://github.com/jesdga95/basalt/pull/112), created **13:42:34Z**, CUDA Q2_0 down kernel 64 rows/block and4 lanes per row, same reduction order and tested bitwise; local glue chain −3% to−13%, example original IQ3_S T4 **103.7→91.6µs**, single CUPTI expert-down 255→185µs/window, **whole RTX5090 Laptop inference within noise** owing to overlapping host experts. Different quant/hardware, no extrapolated owner gains. Both PRs open.

## 2. New Strata issues / benchmarks and source IQ3S admission risk

[Strata #4474](https://github.com/Niko1221/Strata/issues/4474), created **14:12:03Z**, updated14:12:15Z: reporter RTX5080 16GB, Ryzen9950X3D96GB WSL2, engine0.1.53 original GSQ IQ3_S with PLE sidecar/int8 KV/MTP and --vram-reserve-mib700. Expert autosizer reports 2712 slots then expands to3514 (6.72GiB), 44 warnings of 0MiB or low VRAM, repeated identical startups leave free VRAM swinging101–1144MiB; PLE mlock failure could reflect locked-page ulimit, **not proof of RAM shortage**. Root cause unconfirmed, no paired downgrade. **Action:** owner 16GB GPU admission must certify actual reserved free VRAM after complete model + expert + MTP + indexer + scratch load, and at 128K true occupancy, with repeated cold boot stability and conservative reject/rollback when under budget. Do not attribute all to expert autosize without profile.

[Strata #4470](https://github.com/Niko1221/Strata/issues/4470), created14:04:07Z: Windows RTX5080+4060Ti16 in slow-chipset layer split, Ryzen9800X3D32GB, **Coder IQ1_M**, NOT original IQ3_S; stock0.1.52 vs older tuned fork0.1.38: 49.4K prompt PP **228 vs 2354 t/s** and decode depth ~55.9 vs76.7, warm TG59.3 vs tuned93.6. Multiple confounders (engine versions, draft floor, worker count, KV q4_0 vs int8, file I/O ~449GB, full mixed-GPU PCIe topology), **not 10× improvement transferable** to user's single5070Ti. Signifies offload page/memory residency can dominate.

[Strata #4468](https://github.com/Niko1221/Strata/pull/4468) created13:59:08Z: ORIGINAL IQ3S dual RTX3090 PCIe3 split, old Xeon AVX2; one vendor benchmark reports **1127/1610 PP at4K/16K and 114–129 TG**, 12/12 sanity, tuned 26 rounds; opt-in CPU prefill share saved8–13% incremental 300–4000-token prompt reads on this box, not one GPU 5070Ti or M1. Companion [#4473](https://github.com/Niko1221/Strata/issues/4473) created14:11:21Z: benchmark CLI --url can wrongly record **one RTX3090** for an actual two-identical-GPU split, while --profile --no-start captures both. **New requirement:** physical GPU count/per-card memory/split/CPU/quant/PLE effective flags and tool SHA must be attested, not blindly copied from result JSON.

[Strata #4463](https://github.com/Niko1221/Strata/issues/4463) created13:44:21Z: source updater busy-check can miss app-launched model and attempt duplicate giant model load; guard Work/Actions runner against duplicate instance and overcommit. [Strata #4466/4467](https://github.com/Niko1221/Strata/pull/4466), created13:58Z, opt-in conditional refusal control-vector (CUDA; Metal stub) is unrelated to throughput and not relevant to Project51 performance certification. No deployment recommendation.

## 3. New commits after prior cutoff, not model-direct speed result

[TensorFold 33b9b5c](https://github.com/ashhart/TensorFold/commit/33b9b5c0741fe9e58fde65f8d52e2d1b4590b510), **13:52:42Z**, opt-in Qwen3.5 native Metal cross-request RAM prefix retention: copies committed recurrent+convolution+attention+logits state and paged placement to host-owned snapshots; default unchanged without cache budget. Different **Qwen3.5**, no exact QFN owner M1 Metal KVarN/Relay, no measured PP/TG.

[TensorFold 0ecaf339](https://github.com/ashhart/TensorFold/commit/0ecaf339b115b8f6ecc29690d8b0a79504a65531), **13:47:53Z**, different Qwen3.8-27B/Qwen3.5 CUDA attention separate contiguous whole-window path skipping paged metadata; paged/mixed still take paged path, poison-page metadata host checks. No physical benchmark or FlashNext QSA fit proof. Other fresh TensorFold commits13:47–13:52 were launch-contract and changelog updates **restating previously reported FlashNext M3Ultra sampler and NVFP4 CUDA numbers**, not new results.

[vLLM ed6b8f4](https://github.com/vllm-project/vllm/commit/ed6b8f4cd2b47e4240e7ff5feb5105444245b0c2), **13:53:34Z**, newer FlashInfer compatibility for DIFFERENT DeepSeekV4.1 specialized CUDA decode, not native KVarN source improvement.

## 4. Broad mandatory scan / unchanged targets

GitHub connector checked commits and recent issues/PRs with actual API timestamps for Basalt, Strata, oMLX, TensorFold, mlx-serve, llama.cpp, vLLM, paperniuk/ds4, antirez/ds4, BeeLlama and ThermalForge. There were **no new qualifying main commits** in this window for Basalt, Strata, oMLX, mlx-serve, llama.cpp, paperniuk/ds4 (last Oct13), antirez/ds4 (last Oct21), BeeLlama (last Oct14), ThermalForge (last Oct5). Basalt contributions above **OPEN PRs, not merged**. Other GitHub updates are mostly unrelated models or issue comments on older work. Public web searches for ShapeLearn/QFN, source IQ3S, Q8 PLE, M1 fused K4V3 and QFN benchmarks found older Oct4 Paperniuk M1 44t/s/35t/s at400K, older HF cards/benchmarks and generic recipes; **no eligible fresh comparable owner evidence** (web crawl time != measurement date).

**Targets HOLD:** two independent M1Max64 native original GSQ-RCO IQ3S truly occupied128K ≥40TG / ≥425 genuinely cold PP, true262K ≥35TG /≥400 cold PP, 3–5 correct persistent xhigh code agents, AA-like≥38, custom transformer mixed~3.3–3.6 bpw quality matching oQ5e/BF16, oQ4e fast comparator; original PLE IQ4NL vs Q8_0/BF16 quality eval still only proposed. Owner RTX5070Ti16/CoreUltra7265F64 Linux short100–115t/s prediction unmeasured low confidence. RX6800 non-XT16GB VRAM and ONLY16GB host RAM unchanged. No new original source owner QFN true128/262K result, fused Metal K4V3 or ShapeLearn QFN.

**Proposed next checks ONLY:** main+PR114/current RAM patch deep139K A/B with exact owner source, PR113 supervised RAM pressure + cancellation/continuation, 16GB cold-boot VRAM reserve correctness, benchmark topology certificates, prior high-priority source exact Relay, M1 two-pass sampler and Q8 PLE tests. Gate PROPOSED → HIGH-APPROVED → RUNNING → RESULTS → AWAITING-HIGH-REVIEW. No run, daemon, agent, hardware or model mutation authorized. ThermalForge remains optional read-only candidate.

**NEXT HARD FRESHNESS BOUNDARY: 2026-10-28T14:12:42Z.**
