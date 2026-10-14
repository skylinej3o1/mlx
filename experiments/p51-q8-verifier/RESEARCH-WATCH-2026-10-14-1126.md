# Project 51 research watch — 2026-10-14 11:26 EDT

**Previous strict cutoff:** 2026-10-14 11:19:19 UTC.
**New strict cutoff:** 2026-10-14 15:26:39 UTC (user request).
**Classification:** NO NEW VERIFIED CODE/RELEASE EVENTS in the four-hour interval for our top inference/research projects; two **RECOVERED OLDER EVIDENCE** diagnostics improve validation. No device-side test run, no source patch, no certification/target change.

## Research scope and negative checks

- Queried GitHub created dates of PRs and issues `>=2026-10-14`, filtered to `(11:19:19,15:26:39] UTC` for **Strata, oMLX, Basalt, Strata-for-Mac, Sushi, llama.cpp, vLLM, SGLang, mlx-serve, TencentDB-Agent-Memory**. **Zero** qualifying newly created items were returned in that four-hour slice.
- Checked latest default-branch commit dates in **Strata, oMLX, Basalt, Sushi, Strata-for-Mac, mlx-serve, TencentDB, pi-vcc, adaptive-KV-streaming, DS4**. All most recent default-branch commit timestamps were **before 11:19:19 UTC**. This does not exclude unmerged commits to PR feature branches or unrelated source projects.
- Re-checked relevant existing PR state: Strata community IQ3_S 16GB/64GB #2404 still OPEN; oMLX M1 Max-specific kernels #4496 OPEN; oMLX per-API-key KV state partition #4518 OPEN; nonfinite GDN checkpoint #4516 OPEN; DSpark DFlash #4525 OPEN; #4508 batched DFlash and #4509 SSD requeue **already MERGED** in earlier Oct14 checkpoint and remain so. Do not re-count their earlier publication/merge dates.
- GitHub releases/latest: Strata **v0.1.44.1 published 2026-10-14 00:13:09 UTC** remains latest; oMLX latest tagged **v0.7.1.dev1** from Oct9 (the new Oct14 oMLX batched-DFlash/requeue features are in main, not established as a newer tagged release); Basalt returns no latest release. The prior Oct14 07:19 watch already records all material features, Mac RAM guard, Swift Mac non-support, and exact 4080SUPER community benchmark. Do not call these four-hour discoveries.
- Contemporaneous public searches did not identify a **new** exactly matched Swift1.5 **ISTA-DASLab IQ3_S** full 262K/xhigh benchmark on the user's RTX5070Ti/Core Ultra7/64GB, or a DASLABS IQ3_S actual-M1Max64GB full long-context run. Community Sushi-3bpw and oMLX-oQ4e results are different quant/model backends.

## RECOVERED OLDER EVIDENCE: PLE SSD latency masquerading as GPU GDN kernel stall

**NOT a new Oct14 event:** Strata #2239 was opened Oct13; reporter established root cause and before/after data Oct13 09:02–09:22 UTC, and reiterated in GitHub comment Oct14 00:02 UTC, **all before current previous cutoff**.
Source: https://github.com/Niko1221/Strata/issues/2239

- Original 2xRTX2080Ti IQ3_XXS layer-split rig / 157GB RAM shows `hc0 norm` GPU timing **135–213ms/window** and **~9.3–11.6 TG**, superficially implying GPU GDN/SIMT regression. The GPU actually waited on **host-side PLE table row gathers**, reading a 28.8GB lookup table from mergerfs spinning disks at only **222 rows/s** (~1MB/s random 4KiB reads). The first GPU timing stamp incorrectly absorbed upstream host wait.
- Same rig/version and otherwise same configuration, `--ple-io ram` (fits in 157GB host): **80.6–86.8 TG**, fresh 5,065-token PP **640.8→1070.3**. This is **~8× recovery from extremely slow HDD PLE I/O**, NOT a general 8x Metal/5070 speed optimization.
- Our owner 64GB RAM and dual M1 Macs **cannot casually put the full ~28.8GiB PLE table in anonymous host RAM** alongside IQ3_S expert pool, KV/GDN and OS. More relevant method: keep PLE on fast NVMe, measure **random PLE row service rate** at effective I/O backend, resident/hot-row hit rate, host wait and per-window GPU stall separately. Exclude slow-HDD baseline from any Strata/Basalt/oMLX causal comparison. Do not conflate startup bandwidth probe with sustained random lookup performance. Catch mislabelled "GDN kernel" latency.

## RECOVERED OLDER EVIDENCE: 64GB WSL memory reporting can hide Windows host exhaustion

**NOT a new Oct14 finding:** independent 2026-10-12 Japanese report, RTX5070 **12GB** + RTX5060Ti **16GB**, 64GB system, WSL2 Ubuntu assigned 56GB (4GB swap), Strata **v0.1.41**, original DASLABS IQ3_S GGUF, short chat / OpenCode 40,960-token configured context. This is a **dual-GPU split**, *not* the user's RTX5070Ti 16GB single GPU and not filled 262K.
Source: https://murasan-net.com/2026/10/12/strata-qwen-flash-next-iq3s/

- Three short 64-token-prompt runs showed decode **39.8 / 44.9 / 52.2 TG**, with uncertain thinking-token accounting; not long agent TG. GPU expert tier around 7,748 / 24,576 cached slots; 32.08GiB pageable resident CPU experts; respective VRAM 11.4/15.1GiB. No strong ability/xhigh controlled comparison.
- On one initial longer OpenCode task, Windows **free physical RAM 14.36→1.46GiB** and `vmmemWSL 41.48→54.05GiB`; WSL **Cached 5.66→18.41GiB**, but Linux `MemAvailable` stayed ~17.8GiB. Not GPU spill: Windows physical backing of WSL cached file pages was exhausted. The author's safety gate stopped the task.
- Reporter ran under `systemd-run --user --scope -p MemoryHigh=42G -p MemorySwapMax=0 -- <server>`; the comparison long prompt then completed HTTP200 in 98.4s, with Windows free memory minimum 10.58GiB, one observed test. This is a cgroup **reclaim pressure threshold, not a hard physical memory guarantee**. It may hurt throughput and doesn't certify model quality or multiple agents.
- For planned **native headless Linux Lenovo**, this exact WSL double-accounting/host-return issue should not be transferred. But track `MemAvailable`, process RSS, pinned host bytes, Linux page-cache reclaim and SSD faults independently. If testing via WSL/Windows first, track **Windows actual free RAM and vmmemWSL** in addition to Linux counters and set a conservative hard-stop threshold.

## Current deployment choices unchanged

1. **Lenovo RTX5070Ti16GiB / Core Ultra7 265F / 64GiB DDR5-4800:** candidate Strata v0.1.44.1 against pinned 0.1.42 baseline and Basalt Linux Blackwell; compare exact original/Swift DASLABS IQ3_S artifact where runtime conversion supported, MTP on/off, actual filled context 16/64/128/192/near262K, cold PP, sustained TG, xhigh task outcomes, pinned/SSD/VRAM expert provenance, hot PLE rows and agent cache competition. No early-context ~90TG claim at fully filled 262K.
2. **2x M1 Max 64GB:** independent dense 27B lane under oMLX and M1 #4496 optimization remains a better *measured* responsive-agent reference. Original GSQ/DASLABS IQ3_S Mac Strata0.1.44.1 is an *experimental fit/SSD-streaming* test; official Mac IQ3_S guidance ~96GB, Swift Mac not shipped. A full single-Mac ~262K xhigh run and cross-Mac PP2 numerical cert have not been shown. Sushi 3bpw and oMLX oQ4e cannot be renamed DASLABS IQ3_S.
3. **Relay/agent correctness:** exact per-model quant and GDN/decay/KV/indexer/MTP state and ownership, completion fences, buffer lifetimes, role/tool schemas and independent agent session namespaces remain hard gates. oMLX batched DFlash and SSD requeue **main merged**, but pause does not automatically support DFlash. Test independent Macs prior to dual-Mac experimental PP2 or CUDA→Metal state migration.
4. **Quant quality:** keep custom xhigh ~3.3–3.6 transformer bpw mixed-bit research and oQ5e quality comparator; test source-like long agent tasks, not WikiText or isolated MTP greedy identity alone.

**Research target movement: NONE.** Exact-Q8 P58/P61/P69B3/P69B6/P69B11/P69B12 verifier and `RESEARCH-TARGETS.md` unchanged; no hardware purchases; no production rollout from the research watch.

**NEW STRICT HARD RESEARCH BOUNDARY: 2026-10-14 15:26:39 UTC.**
