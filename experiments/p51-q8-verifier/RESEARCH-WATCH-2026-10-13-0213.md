# Project 51 research watch — 2026-10-13 02:13 EDT

Previous hard cutoff: **2026-10-12 20:27:25 UTC**.
New exact cutoff: **2026-10-13 06:13:56 UTC** (user message).
Scope: MiniCPM-V 4.7 from user's r/LocalLLM link; Strata, oMLX, mlx-serve, llama.cpp, vLLM, SGLang, DS4, TencentDB/Pi and adaptive-KV repo. Sources created or substantive measurements strictly within the window count as NEW; merged older PR = UPDATE; old measurements reprinted in new PRs are NOT novel physical receipts. Release issues may be self-reports. URLs below point to source projects.

## Verdict and canonical targets

**The first directly topology-matched external M1 Max (32-core GPU / 64 GB) long-context dense 27B speed report in this watch is a meaningful increase in *experimental-path plausibility*, but it does NOT promote our numeric B2 or B1 targets.** It is one developer's single-Mac MTP-versus-DFlash2+kernel comparison, not a strict same-backend isolated kernel A/B, nor dual-M1 PP2 execution. Keep certified exact-Q8 P58/P61/P69B3/P69B6/P69B11/P69B12, canonical oQ5e xhigh quality comparator, custom mixed-precision Flash transformer target and all `RESEARCH-TARGETS.md` numbers unchanged. Swift-1.5 IQ3_S / 5070 Ti 64 GB filled 128K–262K xhigh still untested on user's exact computer. No new hardware purchases.

## NEW release: OpenBMB MiniCPM-V 4.7 35B-A3B / 1B
Official:
https://huggingface.co/openbmb/MiniCPM-V-4.7-35B-A3B
https://huggingface.co/openbmb/MiniCPM-V-4.7-35B-A3B-gguf
https://huggingface.co/collections/openbmb/minicpm-v-47
https://github.com/OpenBMB/MiniCPM-V/blob/main/docs/minicpm_v4dot7_en.md
User post: https://www.reddit.com/r/LocalLLM/comments/1x493yc/openbmbminicpmv4735ba3b_hugging_face/

35B total / A3B active parameters MoE VLM, Qwen3.5/Qwen3.6 language backbone acknowledged in official model card, SigLIP2 vision module, mixable 4x/16x visual-token compression (intra-ViT), images/multiple images/video in model card, 1B smaller variant; Apache 2.0 weights. Vendor says ~13+ TG on iPhone17 ProMax with ~3GB *runtime memory footprint* using **lookahead expert scheduling (LES)**, fine-grained layer-wise expert quants and DSpark; Reddit cites ~17+ on 16GB M4 iPad. Critically **3GB is not 35B weight storage or total runtime/SSD memory requirement**, and vendor claims are not third-party verified on RTX5070 Ti 16GB, either M1 Max 64GB, or Pi tool-agent tasks.

LES predicts expert IDs ahead but actual original routing is evaluated: prediction only controls prefetch/order, missed experts are still fetched. This is attractive *architecture reading* for our Strata/Relay expert-stream scheduling without sacrificing numerical routing identity. Official GGUF, INT4/AWQ/GPTQ/FP8 and DSpark draft variants exist; compare downloaded exact quant/tower/model weights and runtime compatibility before claiming fit or speed. Vision detail performance tradeoff 4x vs 16x must be evaluated at fine screen text; keep structured OCR/UI element grounding and false-positive controls.

**Recommendation:** **pilot as *vision/screenshot/document/video specialist*** for Playwright and agents, NOT replacement for Swift-1.5 xhigh coding model or Project51 main Flash dual-M1 research target. Stage on currently available 5070 Ti or M1 Max as *separate service* (can swap with existing model; do not claim two 35B models co-resident at 16GB). 1B is a fast screening tier. Evaluate screenshot-based navigation grounding, OCR small text, dense PDFs, UI coordinate errors, chart extraction, video frame tasks against current pipeline; wall-clock TTFT, correct answers and video processing time. DSpark vs no draft; 4x/16x. Initial launch under llama.cpp/Ollama GGUF and actual memory measured. Generic vendor evaluation plots without raw reproducible per-item data are not quality certification.

**NEW implementation evidence:** mlx-serve merged text support commit `7a2a975a` 2026-10-12 21:28 UTC and image support PR #834, merged code commit `15eaaea5` 2026-10-13 05:45 UTC:
https://github.com/ddalcu/mlx-serve/pull/834
Ports SigLIP2 tower, 2x2 merger and crop slicing plus M-RoPE positions into Zig. M5 Max128GB, 23/23 vision smoke cases (tools, two pictures, image prefix cache, OCR-ish page), 3854 tests passed in Zig suite, 4005 in app suite, reference cosine >=0.9993. **Video unsupported by this runtime (returns 400)** although the model advertises video. No M1 Max performance receipt; a text-only 4-bit pack without vision tower cannot inspect screenshots.

## NEW exact M1 Max 64GB report: oMLX PR #4496 (critical)
https://github.com/jundot/omlx/pull/4496
Created 2026-10-12 22:58:23 UTC, **open draft**, approximately 1050 changed lines with 500 lines of tests. Author tested one 32-core GPU M1 Max /64GB, MLX0.32.2/oMLX0.7.0 runtime, memory guard custom ceiling 52 GB, interleaved A/B same session. Three models (Qwen3.8-27B-oQ4e, Qwen3.6-35B-A3B-oQ4, Gemma4 26B-A4B-oQ4e). M1-gen-specific verify qmv (short multi-rows), fp16 skinny QMM for 5–16 rows, chunked MLX SDPA on head_dim256/512, M1 key split attn. All on `applegpu_g13` only; M2+ unaffected.
Qwen3.8-27B **DFlash2 block8** at actual filled 17K/67K/133K, author-reported greedy TG:
- Before upstream MTP **31.3 / 23.8 / 17.6**
- After patched DFlash2 **40.4 / 33.7 / 24.2**, gains ~29/42/38%. **Confounded** by switching MTP-to-DFlash2 and patch; not proof of isolated kernel-only gain. At temp1.0 short-code, MTP **25.8 TG** outperformed patched DFlash2 **16.4 TG**.
Other models (mixed confounds): Qwen3.6 MTP3 17K/34K/67K **75.9/65.6/48.4 -> 93.2/81.3/54.7 TG** but before used different memory tier and MTP auto setting; Gemma4 long prefill 71–103K/103–136K **281/216 -> 305/252 PP**. Some kernel unit precision checks vs fp32, multi-hour coding-agent session (~117K reused prefix); full pinned dependency test suite NOT run, 16 existing failures on app MLX older than repo pins, batch>1 untested.
P51: this is directly comparable physical silicon for **independent per-Mac dense-27B** lane; prioritize oMLX M1 verify kernels and DFlash2 A/B for actual 32/64/128/133K and *sampled coding* tasks. Keep Swift variant, quant, context/MTP acceptance, cache behavior, TTFT/PP/TG and correctness separate. **Does not establish dual-M1 tensor/pipeline handoff or long-context Swift Flash-Next.**
Related #4495 DFlash2 config omitted num_target_layers and silently fell back to no speculation; now proposed fallback to target depth and log loud errors; tested on M1 Max. https://github.com/jundot/omlx/pull/4495

## NEW: more oMLX correctness/performance
- #4500 created **2026-10-13 06:03:34 UTC** just before cutoff: optional 3-bit coarse lm_head draft on *greedy* MTP chains. M4 Max64GB Qwen3.8-27B oQ4e: 4K pooled 47.85->51.59 TG (+7.8%), 16K 42.52->46.62 (+9.6% pooled, but drift and noise); per-cycle gain ~4%; extra ~493MiB resident coarse head, target full-precision verification unchanged but near-tied outputs can differ across verify width. Not measured M1/133K, opt-in `OMLX_MTP_GREEDY_COARSE=1`; no promotion. https://github.com/jundot/omlx/pull/4500
- #4493 created 2026-10-12 22:18 UTC: **more-compact oQ4e-fp16-mtp Flash-Next** 70.5GB resident on M5Max128GB only reached ~65K usable prompt vs older oQ5e 84.2GB resident with ~256K usable under different pack path; external prefill guard predicts ~19.7GB transient. This is reported, not controlled causal test; **main merged commit 89a40d1131 2026-10-13 02:25 UTC** fixes fp16 Flash-Next PLE reads staying fp16 from SSD; retest before blaming quant itself. Robust lesson: resident **model footprint is not viable context or peak prefill footprint**.
  https://github.com/jundot/omlx/issues/4493
- #4492 created 2026-10-12 21:23 UTC: sub-4096-token hybrid prefix lookup races async boundary store; developer reproduces 888–963 token same-prefix instant repeat MISS TTFT ~5 sec vs ~50ms gap HIT ~0.37 sec on M2 Max. Actual 13-day logs 4 fast-extending pairs all HIT: rare synthetic race. Main commits **a789c89ac0** and **c756df2a5a** at 2026-10-13 04:57–04:58 UTC fix sub-block waiting/side snapshots. No exact user's Mac proof.
  https://github.com/jundot/omlx/issues/4492
- Other oMLX #4478–#4489 SSD pressure park stack remains OPEN at cutoff; not part of main M1 results or production. 
- No direct production proof of external oMLX <-> Strata CUDA state transfer.

## NEW RTX5070Ti /64GB v0.1.43.1 quant class benchmark #2173
https://github.com/Niko1221/Strata/pull/2173 (created 2026-10-12 21:38 UTC).
RTX 5070Ti 16GB, Threadripper7960X 24-core AVX512, 64GB host, Windows11, NVMe, original Flash-Next native IQ2_XS/IQ3_XXS/IQ3_S, configured 65,536 context with 32,768 resident KV window, greedy/think OFF. Stock 3-run suite:
- short-chat TG **123.6 /115.0 /96.3** (respective quants);
- fresh16K PP **3287/3473/3448**;
- fresh32K PP **3320/3474/3458**;
- agent followup TG **130.0/126.3/102.2** with actual final-turn ~14.5K and ~68.7% cached.
No correctness, no filled 65K/128K/262K, different CPU/storage/thermal, original rather than Swift, not xhigh. Best same GPU + host-capacity flash original class receipt this window; do not promote user's CoreUltra7-265F Swift throughput.
RTX5060Ti 16GB +64GB report #2202 0.1.43.1 IQ3_S: short54.7 TG/16K1761 PP, 14.4K agent58.2 TG, speed-only different GPU/CPU. https://github.com/Niko1221/Strata/issues/2202
Potential non-regression issue #2167 (created 20:59 UTC) plain 0.1.43 and hotfix 0.1.43.1 still slower/truncate some content vs 0.1.42 on RTX5090 Windows IQ3_S: exact tool-text boundary reported, no minimal machine-independent reproduction. Keep output integrity regression suite and **pin v0.1.42**. https://github.com/Niko1221/Strata/issues/2167

## NEW concurrency and cache-state reports
- Strata #2234 (created 2026-10-13 05:49 UTC) opt-in `STRATA_BATCH_ATTN_ROWS=1` and `STRATA_BATCH_GDN_GROUPS=1` remove per-row GPU launch overhead for active slots. RTX PRO 6000 96GB all experts VRAM, four clients batch4 **268.4->311.7 aggregate TG**; eight clients batch8 **308.4->374.8**, with 4 greedy parity prompts. Single request neutral/possibly slower; KV-streaming path retains old kernels; no RTX5070Ti offload or M1 direct transfer. https://github.com/Niko1221/Strata/pull/2234
- Strata #2228 (created 04:19 UTC): on 0.1.43.1 / RTX4090D48GB Windows/128GB, long screenshot agent with *pure append-only* prompts still restores 32768-token-grid coarse checkpoints and reprocesses 6.8K–47K input tokens; 13 occurrences over 3.5h and **4–17 sec TTFT**; deep turn checkpoints existed elsewhere. Warning: don't count session-cache presence as reliable next-turn retention; add exact append-only remote-agent replay with raw message hashes, cache logs, per-turn checkpoint frontier and full TTFT. https://github.com/Niko1221/Strata/issues/2228
- Strata #2227 (created 04:05 UTC): 4090D sm89 48GB original IQ3_XXS with `--mtp-hnorm stream` versus pooled changed acceptance 82%->86% and TG ~220->228 at actual6K, 203->208 at70K; neutral at120K. Same token outputs greedy checks. Different GPU/model and uncertainty; include in MTP ablations only. https://github.com/Niko1221/Strata/issues/2227
- vLLM #61309 new RecoverSSM Qwen3.5/Next; SGLang #43966 retains routed expert history on KV retraction; source artifacts reinforce recurrent-state/prefix/rollback accounting as cross-engine gates. No proof Relay is implemented.
- mlx-serve #831 created 2026-10-12 20:34 UTC: lossy `--mtp-typical 0.2 --mtp-greedy-tail` Flash-Next agent sometimes loops as MTP accept ~95%, when unmodified exact version doesn't. Reporter saw 13 loop guard cuts /10163 lossy requests vs 0/12297 exact, but sessions/nonpaired samples; no proof causal quality without controls. **Do not enable approximate acceptance** solely for high TG; grade repeated tool calls, loops, answer pass rate and stuck budgets. https://github.com/ddalcu/mlx-serve/issues/831

## Current practical topology plan / no replacement
- Primary: frozen P51 verifier exact-Q8 and quality gate; large Flash custom ~3.3–3.6 transformer BPW with oQ5e reference; on Lenovo Strata 0.1.42 pinned versus 0.1.43.1 experimentally, FS off, long xhigh correct-task scoring; no new hardware.
- Per Mac: independent Qwen3.8-27B agent baseline with oMLX M1-specific DFlash/verify kernel opt-in after sandbox qualification, project-51 PP2 still research. No automatic promotion based on author speed numbers.
- MiniCPM 4.7 separate vision-oriented VLM (screenshots/OCR/video where supported) on one machine or 1B fallback. Do **not** assume its advertised iPhone phone memory number is weight storage or that all backends serve video.
- For all 3–5 agents: explicit parser/output length QA, memory-park semantics, cross-agent namespace/lease identity, end-to-end wall time and attention/KV capacity ledger.

## Negative checks
- DS4 PR/issues during window: no newly created direct M1 PP2 speed changes; earlier ROCm10.1 Strix Halo PR #1210 already in previous watch.
- Pi-vcc and RaymondHuang adaptive KV Streaming V2 latest Oct12/Oct11 repo code/PR status not materially advanced in this window; earlier audits continue to apply.
- TencentDB-Agent-Memory's Pi support in October9 v2.0.2 is an existing alternative app-memory framework and not physical KV. No demonstrated direct CUDA->Metal state transfer or Project51 2-lane throughput from its release.
- No independent benchmark proves MiniCPM 4.7 35B vision agent performance on M1 Max64 or RTX5070Ti16 at native full 16x/4x in this window.
- Official Strata latest checked **v0.1.43.1**; all new performance PRs OPEN, not released tuning defaults.

**Hard boundary advanced to 2026-10-13 06:13:56 UTC**.
