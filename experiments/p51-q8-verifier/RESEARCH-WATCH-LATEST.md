# Project 51 / Relay — LATEST research watch, October 23 2026, 22:39 EDT

**Previous verified branch HEAD:** `2f4812c4b5ad2bec0a186252fffe950b3b47ab03`.
**Previous UTC cutoff:** **2026-10-23 20:32:52Z**.
**NEW strict UTC cutoff:** **2026-10-24 02:39:58Z** (October 23, 22:39:58 EDT). Next scan starts strictly AFTER this instant.
**Full research report:** [RESEARCH-WATCH-2026-10-23-2239.md](./RESEARCH-WATCH-2026-10-23-2239.md). Previous [16:32 watch](./RESEARCH-WATCH-2026-10-23-1632.md), [13:47 supplement](./RESEARCH-WATCH-2026-10-23-1347.md), [07:19 watch](./RESEARCH-WATCH-2026-10-23-0719.md).

## New evidence (merges, machines, scope distinguished)

- **NEW DS4 #1267 OPEN at00:43Z** real **M5Ultra256** *DeepSeek-V4.1* 1M-row Metal indexer kernel **7.93→2.89ms (2.75× component)**, standalone 1M decode12.54→13.38TG (+6.7%), 4K~27.3 unchanged. A local unmerged stack with older #1261/#1262 (opened Oct23 15:24Z, before prior cutoff) gives 1M27.14→31.55TG and context tax -28.4→-15.6%. Source exact selection tests but NOT M1Max64 QFN FlashNext; 3 PRs NOT merged, two conflict.
- **NEW oMLX #4801 DRAFT** M3Ultra512 GLM5-next short-query sparse score-stage **0.979→0.489ms @~16K, 3.384→0.754 @~128K, 13.304→1.672ms @~262K (7.96× stage only)**. Actual173GiB GLM checkpoint failed to load; NO full-model TG proof, not M1 or source QFN.
- **UPDATED OLD Strata #3584 OPEN** RTX3090 IQ3XXS source prefix mount + checkpoint ladder, 16-turn edits **234.2→162.4s (-31%)**, identical16 answers (14/16 correct both), mid-edit reuse55–57%, replay99.9% /0.2s. Speed comparison from older base carried forward; rebase tests passed, **no Metal/M1 native full128K agent proof**.
- **UPDATED OLD llama.cpp #30594 OPEN** hybrid CPU+GPU missed experts RTX4060Laptop8GB Qwen3.5 MoE Q6K 22.5→37.7TG (1.68×), small GPU expert cache. NEGATIVE when nearly all experts fit (L4) or community 4070Super; not original QFN+owner64GB fit.
- **UPDATED old llama.cpp #30792** physical **gfx1151** Q8 KV direct-tile vs FP16 scratch, at ~63K read **31.19→50.51TG (+62%)** and FP16K+Q8V27.88→49.38 (+77%), FP16 control same. No gfx1030 RX6800/FlashNext sparse support.
- **NEW Basalt #39** RTX5090 500W/62GB RAM physical IQ3S **PP16K8859/PP64K9501/decode374.8** vs IQ3XXS **8784/9326/564.5**, NVFP4 **9289/10095/305.4**, differing quant quality and expert resident bytes. Not owner5070Ti16 or xhigh.
- **UPDATED TF #1113** still draft EXL3 two CUDA16GB ranks with BF16 KV host paging and agent snapshots; real 2×200K not qualified, graphs no speed proof.
- **KVarN follow-up:** **no new direct original QFN IQ3S KVarN4-versus-Q4 comparison**. Huawei main last commit June20; Anbeeld BeeLlama Oct14; valujin branch Sept3. Previous Qwen3.6 dense 27B RTX3090 64K same1024 exact tail KVarN4 median KL0.000994 vs Q4_0 0.001057; 1232 vs1248MiB; TG25 vs24.1 @64K. Earlier result only, not a new Project51 score. Huawei default K4V2/K4V4, NOT K4V3 registered.
- NEW oMLX #4806 M3Ultra MiniMax decode1.14×/1.2× with exact outputs, NEW #4808 M5Ultra V4 prefill1.19× with one near-tie answer flip. Neither owner M1 or source QFN. Unmerged old TF EXL3 prompt PRs closed; no new owner native K4V3 262K or exact Relay.

**Frozen hardware and targets:** 2 physically separate M1Max64 32GPU each, general ISTA-DASLab Qwen3.8-Flash-Next GSQ-RCO IQ3S genuinely occupied128K >=40 sustained B1TG /425 genuine coldPP; occupied native262K >=35/400; source-like xhigh AA-like>=38; 3–5 independent retained coding agents. RTX5070Ti16+64DDR5 Linux separate; RX6800 nonXT gfx1030 16+32DDR4 separate. No third Mac; no numeric target/probability changes.

**Next experiments:** physical original-QFN DS4 M1 128/262K memory and source-quality; native KVarN4/Q4/F16 paired QSA selection/fidelity; exact 3–5 session cold/resume; correct hardware CPU/GPU hybrid/AMD lower quant tests; complete committed QSA/GDN/PLE/MTP CUDA→Metal Relay measured with TB4.
