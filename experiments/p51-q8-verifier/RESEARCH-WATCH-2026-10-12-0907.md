# Project 51 research watch — 2026-10-12 09:07 ET

Strict previous boundary: **2026-10-04 22:06:41 UTC** (the previous `RESEARCH-WATCH-LATEST.md`).
New evidence/documentation cutoff: **2026-10-12 13:07:45 UTC**.
Nature of update: **cumulative true-up of verified Oct 5–12 external research and Oct 12 code audit**. Public upstream receipts and selected new source/PR checks; **not a claim of an exhaustive issue-by-issue replay of every GitHub project**.

## Canonical decision

**No promotion of Project 51 P69 verifier code, no change to the exact-Q8 certified champion, and no numerical promotion of canonical M1/5070/DS4 TG, cold-PP, xhigh-quality, fit or stability targets.** Existing `RESEARCH-TARGETS.md`, `CURRENT.md` and runtime-gated verifier lineage remain the controlling baselines.

The new evidence materially improves **test prioritization** and highlights opt-in CUDA controls, Pi-agent compaction correctness, recurrent/KV ownership, Mac server integration, and context-normalized benchmark reporting.

**Never conflate**:
- context capacity configured vs tokens actually in the attended prompt vs KV held in GPU vs KV retained for subsequent turns;
- original Flash-Next vs Swift-1.5 vs dense 27B;
- low-reasoning/no-thinking speed tests vs xhigh-quality end-to-end coding tasks;
- a 96-GB 5070 Ti host vs the user's **64-GB DDR5-4800 Lenovo**, even with the same GPU;
- speculative *generation* TG vs complete cold-request time and task pass rate.

## NEW / UPDATED: Strata RTX 5070 Ti performance, qualification and regressions

- **Strata v0.1.43 overlap:** issue #2010 / draft PR #2011 now include an isolated `STRATA_ADAPT_OVERLAP` A/B on RTX 5070 Ti 16GB / Ryzen 7 7700 / 93GB DDR5 / native Flash IQ3_S. Same engine default: **68.4 TG**; overlap disabled: **86.4 TG** (+26.3%), ~300-output-token short-context trials. This is hardware-class evidence, **not** proof for the user's 64GB/long-context run; set `STRATA_ADAPT_OVERLAP=0` as the first opt-in A/B on 0.1.43 and pin a v0.1.42 reference.
  - https://github.com/Niko1221/Strata/pull/2011
  - https://github.com/Niko1221/Strata/issues/2010
- **Full context is not necessarily slow, but cross-machine evidence is heterogeneous:** #791 RTX5070Ti IQ3_S / Core Ultra 7 265K / 96GB reported **99.4 TG at 16K** and **99.1 TG at 131K** in limited-repeat benchmark; #775 different RTX5070Ti / 96GB, 257,630-token tuned benchmark reported **43–53.5 TG** depending on cold/warm/profile configuration. Neither is the owner's Swift-1.5 IQ3_S / 64GB / xhigh at 262K; our early-context ~90-TG hypothesis **must not** be relabeled a filled-262K target.
  - https://github.com/Niko1221/Strata/issues/791
  - https://github.com/Niko1221/Strata/issues/775
- **Exact 5070Ti + 64GB class:** #2053 native Flash IQ2_XS/IQ3_XXS / Ryzen 5600G / 64GB shows short-chat **81.9/66.4 TG** and fresh-16K **2177/1945 PP**. 32K/65K configured test arms do not qualify filled 262K Swift.
  - https://github.com/Niko1221/Strata/pull/2053
- **Release regression still unresolved:** #1964 decode loss after v0.1.42->0.1.43; #1975 adaptive-overlap regression; #2038 CUDA dual-3090 split scheduling regression; #2101 PLE `direct`->`mmap` automatic decision slowdowns. Test `STRATA_ADAPT_OVERLAP=0`, record effective `--ple-io`, validate single vs split paths and compare full-task outputs.
  - https://github.com/Niko1221/Strata/issues/1964
  - https://github.com/Niko1221/Strata/issues/1975
  - https://github.com/Niko1221/Strata/issues/2038
  - https://github.com/Niko1221/Strata/issues/2101
- **MTP break-even:** #2045 RTX3070 GSQ-RCO IQ3_S finds MTP-off faster for fresh 48K–128K prompts ending in ~1K output; extrapolated output threshold does not fit the 128K budget. Do not rank engines by TG alone for control decisions; add total TTFT+TG/answer length and correct-outcome comparison.
  - https://github.com/Niko1221/Strata/pull/2045

## UPDATED: cross-backend state and multi-agent scheduling

- **CUDA/Metal precedent:** merged llama.cpp #26004 has a reported GB10 CUDA -> M3 Ultra Metal checkpoint restoration for a hybrid model. It is **not** Swift Flash / Strata CUDA -> MLX Relay export; requires same-model semantics, numerical checks, recurrent GDN, QSA/KV, indexer/PLE and MTP state.
  - https://github.com/ggml-org/llama.cpp/pull/26004
- **Strata early cross-engine probe:** #1990 puts Strata gateway over llama.cpp token engine with Metal MTP draft + NVIDIA target. Reported direct target 6.40 TG vs Metal draft 5.61 TG (slower). Interop proof, no decode handoff or Project 51 PP2 proof.
  - https://github.com/Niko1221/Strata/pull/1990
- **Checkpointing:** #1937 disk-spilled conversations, #1959 scattered checkpoints for edited older prefixes, #2077 persistent common prompt root across restart, #2098 version-gated cache blobs. Distinct scopes, mostly unmerged. Persist only complete, identity-validated state; treat old-build blob reuse as dangerous, and ensure restore cannot extend past committed frontier.
  - https://github.com/Niko1221/Strata/pull/1937
  - https://github.com/Niko1221/Strata/pull/1959
  - https://github.com/Niko1221/Strata/pull/2077
  - https://github.com/Niko1221/Strata/pull/2098
- **Multi-agent economics:** #2099 14.8K sibling shared prefix had 0% reuse when below 16,384 periodic checkpoint; `--prompt-cache-tail` achieved **93.4% reuse** and ~**11.7x later-sibling prefill speed** on a GTX1080Ti. #2050 chunked prefill on 2x5090 reduces a long-running stream stall **12.2->4.2s** (32K pieces) at the cost of a later incoming TTFT. Neither is a TG uplift claim for the user's fleet.
  - https://github.com/Niko1221/Strata/issues/2099
  - https://github.com/Niko1221/Strata/pull/2050
- **Branching contexts:** #2094 correctness/recovery progress, but **50.35s branching API vs 42.12s unmodified** for eight serial calls. Keep as experimental, not a proven latency win.
  - https://github.com/Niko1221/Strata/pull/2094

## NEW: M1 Mac control plane, MTP and prefix restoration

- **oMLX #4447 merged Oct 12:** Splash/Splash-M1 can run as supervised external inference backend under oMLX model/APIs and admission/lifecycle interface. Author's **M3 Ultra** test with Splash 1.3.1, dense 27B and DFlash2 had favorable greedy code TG; no user M1 Max + Swift validation. Require engine launcher compatibility and actual Mac runs; do not assume an early Splash-M1 binary is compatible with 1.3+ interface.
  - https://github.com/jundot/omlx/pull/4447
- **oMLX #4408 merged:** M4 Max dense 27B with MTP/TurboQuant4 attention improvement at actual 16K **21.2->32.6 TG** and 32K **20.5->31.8 TG**. No M1 long-262K numeric transfer. #4442 restores TQ prefix as temporary dense KV for multi-chunk suffix prefill when memory allows; #4453 repairs multi-row left-padding and MTP verify correctness.
  - https://github.com/jundot/omlx/pull/4408
  - https://github.com/jundot/omlx/pull/4442
  - https://github.com/jundot/omlx/pull/4453
- **Operational staging:** one independent dense Swift agent per 64GB Mac is the deployment minimum; oMLX native and Splash-M1 are A/B backends, not evidence of native PP2. Preserve existing dual-M1 exact-Q8 verifier champion and its validator gates while comparing routes.

## NEW: code audit — Pi conversation compaction and CUDA adaptive KV

Detailed reproducible design/limitations:
`REPO-AUDIT-2026-10-12-PI-VCC-ADAPTIVE-KV.md`

- **pi-vcc 0.10.1:** deterministic Pi summarizer, ranked structured facts and searchable original session JSONL. Internal median ranked weighted fact recall **69.2%** vs **72.0% prior pi-vcc baseline**, **~1.4x** fact-density. Not an LLM-compaction benchmark. Manual `/pi-vcc` with `overrideDefaultCompaction: false` only until adversarial agent constraints and tool/failure recall pass. Merged fix #49 addresses Pi 1.1 context edits.
  - https://github.com/sting8k/pi-vcc
  - https://github.com/sting8k/pi-vcc/pull/49
- **Adaptive KV Streaming V2:** a llama.cpp CUDA fork keeps full Qwen3.8-27B attention KV in pinned CPU RAM and streams bounded GPU resident/ring pages; separate MTP host history and lease, recurrent-state rollback. **Only** single RTX5070Ti serial UD-IQ4_XS 27B Q8_0/Q4_0 tested. Historical V2 near-256K: **8.73 TG MTP off vs 19.12 TG MTP depth3**. Subsequent upstream rebase: **69.96 TG at 96K / 54.06 at 128K / 28.51 at 192K**, depth3. **Do not splice different revisions**, call an arena bound total VRAM bound, transfer dense-to-Flash speed, or call it Mac/Metal support. Multi-GPU #2 open.
  - https://github.com/RaymondHuang210129/llama.cpp-adaptive-kv-streaming
  - https://github.com/RaymondHuang210129/llama.cpp-adaptive-kv-streaming/pull/2

## Next evidence gates — no promotion from this watch

1. User Lenovo RTX5070Ti16GB/Core Ultra7 265F/64GB DDR5-4800: pin Strata 0.1.42 vs 0.1.43; one-switch ABBA overlap/PLE/calibration; report committed RAM, pinned RAM, VRAM, GGUF/PLE residence, TTFT/cold PP, decode and quality, at filled **8K/32K/64K/128K/192K/near262K**.
2. Explicit **original Flash vs Swift-1.5**, **IQ3_S vs IQ3_XXS**, **no-thinking vs xhigh** labels and MTP on/off controls. No near-262K promises based on 96GB third-party rigs.
3. Two M1 Max servers: benchmark oMLX TurboQuant + Lightning MTP and separately Splash-M1 on the *same actual model/context* before attempting Project 51 PP2. Keep exact verifier proof and dual-ABI validation unchanged.
4. Relay state portability: export/import precise GDN/recurrent, attention KV, QSA/indexer, MTP and prompt chronology with independent cross-backend oracle; fail closed on mismatched model/runtime/checkpoint geometry.
5. Pi fan-out: verify saved-prefix placement, independent private tails, failed-turn retries and multi-agent correctness; test pi-vcc manual mode before allowing automatic compaction.

## Target movement / provenance

**None.** Certified P58/P61/P69B3/P69B6/P69B11/P69B12 verifier lineage unchanged; no new physical dual-M1 PP2 decode receipt, no user's-own Swift Flash 262K xhigh TG measurement, no cross CUDA->Apple Flash replay. `RESEARCH-TARGETS.md` retained unchanged.

This dated note is the **new hard GitHub research boundary at 2026-10-12 13:07:45 UTC**. The separate Local LLM Fleet cumulative research master v0.74 and October 12 repository-audit artifact remain supporting archives; this branch note records decision-relevant findings rather than copying 1+ MB of conversation history.
