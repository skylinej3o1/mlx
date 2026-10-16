# Project 51 / Relay — focused research watch 2026-10-16 10:10 EDT

**PREVIOUS STRICT CUTOFF:** 2026-10-16 09:39:54 UTC.
**NEW STRICT CUTOFF:** 2026-10-16 14:10:00 UTC (user request at 10:10 EDT). Public items or log timestamps after this instant do not qualify as same-window measurements.
**Method:** Read `RESEARCH-STATE.md`, `RESEARCH-TARGETS.md`, `RESEARCH-WATCH-LATEST.md` first; compared live GitHub source/issue/PR information and author-maintained HF/Agention model cards. Labels: NEW = newly created within window; UPDATE = in-window new evidence/status; RECOVERED OLDER = older material analyzed now, NOT a new publication. Author benchmarks are **not** owner-device measurements. OPEN != merged != released; configured max context != filled context. This is research only; no code, target, verifier, weights, or owner GPU tests.

## Executive verdict

1. **NEW exact GPU/RAM class counterexample:** Strata #2772, RTX 5070 Ti 16 GiB + 63.8 GiB Windows, Flash-Next IQ3_S, Strata 0.1.43.1 default install: short chat **38.1 TG** (32.6–42.9), fresh 4,019 PP **931.9**, fresh 16,058 PP **1199.6**, 14.4K-token agent turns **42.2 TG**, 68.5% cached. Despite `--max-context 262144`, **no real >16K prompt / 200K–262K admission, task quality, or long-output decode was tested**. CPU i5-13600KF, Windows 10; drivers, actual MTP details, calibrated pool/PCIe, RAM pressure, and background loads insufficiently reported. This does not disprove older tuned exact-5070/96GB Linux 95–100 TG at <=131K (Strata #791), and does not certify the owner's Intel 265F + 64GB native262K. It DOES raise urgency of testing untuned versus deliberately calibrated profiles on the actual 64GB host. Do **not** lower target probability from an unmatched experiment.
2. **NEW safe methodological lessons:** Strata #2761 `STRATA_MTP_ROOM_MIN` reuses decode-only MTP expert GPU room for long prefill but measured *slower* total prompt read on 4 mixed GPUs (3,080-token **20.65s room vs 16.17s standing**, 14,859-token **39.81 vs 35.79s**) because open/close PCIe transfer plus relayout costs ~3.4–4.0s; OPEN, no 5070 credit. #2751 `STRATA_POOL_FUSED=1` reduces *CPU microbench* per-layer time ~8–11% on Zen2; the reported +2.1% engine TG is confounded with an additional kernel change, and no Intel 265F/CUDA measurement exists. Both stay opt-in A/B only.
3. **NEW Mac long-context correctness gate:** Strata #2767 demonstrates `--rope-scaling yarn --rope-scale 4` is accepted/logged on Metal but does **not** change actual RoPE angles in reported M5 Max / 86-request greedy comparison. Problem is relevant to *extended beyond-native* scaling, not native 262144; OPEN fix described but not verified landed. oMLX #4606 reports Swift1.5 FlashNext 74K+ session returning just **one 4096-token cached block** after a pause, despite 90.3% steady-state cache hit; volatile early prompt material is a plausible parent-hash chain break. Account for mixed hardware description (M4 Max128 field vs 96GB in body) and a pasted **16:09 UTC log AFTER cutoff**; only earlier 12:53 example is temporally admissible. No proof that engine randomly evicts cache or that a fix is shipped.
4. **NEW parser safety candidate:** oMLX #4613 OPEN at 14:02:41Z proposes returning cap-truncated, unterminated Qwen tool-call envelopes as text with `finish_reason=length` instead of fabricated tool calls / parse errors. Unit and synthetic streaming e2e reported; no live long coding-agent trial. Do not score the retained text as successful tool execution.
5. **RECOVERED older (not Oct16 releases):** Agention's Aug24 adaptive draft-length writeup and existing Gyro/Signal cards. Gyro-S/M/L encode updates last noted Oct10–13; **Gyro Signal still marked coming**, not a verified downloadable combined post-train+rotor+GSQ-RCO pack. No defensible immediate replacement for Swift1.5 IQ3_S.

## Exact hardware transfer audit

### RTX 5070 Ti + 64GB; primary Swift1.5 IQ3_S / Strata

- NEW Strata #2772: actual 16K prefill ~1.20K and short ~38 TG at *configured* 262K. Quant labeled `qwen3.8-flash-next-iq3_s`, not explicitly pinned to the complete Swift1.5-GSQ-RCO source/quant/runtime identity, and tiny generated caps 24/64/100 mean no sustained reasoning/xhigh speed or reliability inference. Same-GPU+RAM is useful admission/default-config calibration; host CPU and config differ. Reproduce raw and tuned with exact revision, compiled CUDA/nvcc, `--mtp` and acceptance statistics, expert cache/VRAM headroom, pinned RAM, actual prompt depths 16K/64K/128K/200K/~262K plus 4K+ outputs and agent solves/hr.
- NEW #2751 CPU expert fused overlap has 0.525–0.526 -> 0.469 ms per IQ3_S/IQ4_NL layer in a **Zen2 CPU-only microbench** (one hash equal across 300 layers), **not a 10% owner CUDA TG gain**. Test A/B only once target correctness stable; Intel Core Ultra 265F memory bandwidth, hybrid scheduler, and architecture may differ.
- NEW #2761 borrowing 672–708MiB of MTP expert memory during prefill is a tempting admission workaround but physical 4-GPU result is negative once reload/PCIe is counted. Do not turn on in production; test only if exact 5070 full-context prefill *fails from ring workspace* and compare full TTFT, not inner kernel speed.
- No verified Oct16 Swift1.5 GSQ-RCO IQ3_S fresh pack, independent ByteShape 3.2/3.8-bpw high-quality winner, or exact owner-native 262K pass established. The older 5070 96GB ~100 TG and 64GB Windows short-depth #832 measurements remain separate calibration rows.

### RX 6800 16GB / gfx1030

- NEW Strata #2773 OPEN 13:49Z: Windows **RX7900XTX gfx1100 24GB**, FlashNext IQ2_XS + MTP and opt-in HIP prefill switches: chat 75.7 TG, 16K PP 1,982.9, agent 82.3 TG; prefill ~10.9K fell 14.1->7.0s under a combined tuning stack. Speed-only single sitting, no quality A/B, different RDNA generation and available VRAM. This supports investigating overlapped/fused HIP prompt paths but **no numeric transfer to RX6800 gfx1030**, whose first job remains speculation-OFF reproducible PP and verifier/frontier parity.
- No exact RX6800 128K/262K, new two-GPU CUDA+HIP portable state handoff or resident-quality result.

### M1 Max 64GB pair (TB4)

- NEW Strata Metal #2767 RoPE knobs misleading for beyond-native scaling, not a reason to demand Yarn for native 262K. Test direct logfile and actual logit changes if experimenting beyond native.
- NEW oMLX #4606 is an application-cache-key ordering warning. Keep static system/tool/repo prefix invariant; append timestamps, changing repository state or volatile tool context **after** the reusable prefix, unless semantics explicitly require earlier ordering. Never wildcard an early token in a cryptographic prefix chain without protecting content identity and cache correctness. Qualify Pi-agent pause/resume after 74K using actual `cached_tokens`, SSD restore bytes and whole-request TTFT. Pending report, not upstream fix.
- NEW oMLX #4609 reports M2 Ultra 128GB / v0.7.1rc1 / dense27B oQ8e-fp16 MTP batch4 attempting 960 threads against max896, no issue with B1, MTP OFF B4, or another oQ8e model in this reporter's runs: configuration-specific bug, not all Flash M1 models. #4608 claims concurrent FlashNext/MTP batch median(empty) crash but contains **19:30Z–19:37Z future-dated logs relative to this strict cutoff**; DO NOT promote those as verified in-window physical events. No known stable release fix from these issue reports.
- Carry forward previous watch's newly merged (08:51/08:55Z **before this window**) oMLX #4603 pooled-buffer prefill fix, #4210 M1Max64GB optional Flash shared-buffer staging +5–7.5% with MTP OFF; do not reclassify as NEW or stack on B1/B4/128K numbers. Stable/control plus patched test builds, MTP OFF first.
- Dual-M1 FlashNext ~40 TG / 400 PP at ~128K remains a **target, not measurement**. No validated complete CUDA->Metal cross-host QSA+GDN+SSM+PLE state transfer; no authority to migrate between unlike Swift/Signal/ThinkingCap checkpoints even if architecture shapes match.

## Agention Gyro, Signal, adaptive speculation: what the evidence does and does not say

**RECOVERED older official cards** (author-reported, not independent):
- Gyro uses custom **Agention Precision Rotor (APR)** rotated expert representation and bespoke kernels/encoder. `TQ1_0/TQ2_0/TQ3_0` Hub labels are size classes, **not stock GGUF ternary formats**. Public documentation is insufficient to call it a verified drop-in Hadamard+trellis implementation or prove its proprietary calibration recipe combines with RCO/ByteShape. Current production runtimes are the Agention llama.cpp fork or **Strata rc1 fork**; **Metal path unproven**. Qwen Flash Gyro-S 27.64GiB GPU weights, M 34.98GiB, L 50.21GiB; S at 128K **30.2GiB measured/claimed** without draft; 256K **~33.3GiB extrapolated**. All exceed 5070Ti/RX6800 16GiB without CPU experts/cache. On one M1 Max, M/L GPU residency might fit numerically, **but kernel and Metal availability and full 128K+ RAM are not certified**.
- Updated author held-out KLD (lower better): Gyro-S **0.401**, M **0.291**, L **0.146** (L updated Oct13, ~108GB file with an 8-bit n-gram table on disk). Original source-comparison quant/routing paths and 60x2048-style evaluations not an agent accuracy certification. Gyro-M **30/30 on selected LiveCodeBench prompts at 128K vs 90% at 64K**, author's small 30-question sample, not full benchmark; no sample-efficient confidence. Author RTX5090 221 TG / ~4883 PP is fully VRAM-resident different hardware. Gyro-M quality/GiB is **worth testing**, but only as alternative artifact rather than mixing the percentage wins of unrelated packs.
- **Signal FlashNext (older)** author Q4_K_XL tier ~67GiB resident weights, AP-IQ4_XS ~57GiB, not Gyro-M 35GiB; no current 16GB or native M1 Metal-fit Signal Gyro. Author reports 10 Terminal-Bench2 tasks, **8/10 base vs 10/10 Signal**, 25% lower wall on mutually solved tasks, 15% fewer tokens, one trial/task; claimed MTP draft acceptance **69%->90%** on coding. MATH500 subset 120 items 97.5%->99.2%, mean thinking 1240->919 (-26%) but median 242->228 (-6%). AIME25 base 25/30 vs Signal 23/30 and **sampling/MTP arms are not matched**, so NOT evidence of superiority on all tasks; high-variance small trials and hardness shift require xhigh tool audit. The base MTP head is retained yet agreement can change after new target logits: independently verify draft acceptance rather than assuming it.
- **Signal dense27B (older)** own card's updated GGUF numbers: **-25% answer tokens / -41% thinking tokens**, and 40-chat MTP-on batch total wall **-19%** and median wall **-28%**; earlier **-57%/-52%** claims describe a PRE-2026-09-13 checkpoint and must not be copied onto updated weights. Existing ThinkingCap27B -37.2% reasoning tokens for 86.6->85.8 macro remains separate; none is canonical Swift source behavior. Quality-first test for real coding tasks with same turn budget and tools before promotion.
- **Adaptive speculation writeup dated 2026-08-24:** Qwen3.8-27B + DFlash2 **on Radeon 8060S Strix Halo Vulkan**, *fixed depth7 20.2 TG / 18% acceptance vs adapt n_max7 65.6 TG / 96% acceptance* (3.2x against a particularly poor fixed-depth arm). MTP is much more costly; Agention explicitly required further fork-specific pipeline work for its up-to-40-TG Flash MTP result. This is **not** a measured 3.2x gain on 5070Ti Strata, oMLX M1 Metal or Gyro, and 96% is conditional acceptance among proposed drafts, not all tokens from all tasks.
- An appropriate controller optimizes **successful tokens per total wall-clock and task completion**, considering draft forward, verification shape, synchronization, rollback, CPU/cache contention and sampled output. Compare target-only, fixed 2/4, adaptive and zero-draft parking per **B1/B2/B4** and context 16K,64K,128K,200K,262K; record proposed/accepted per slot, per-round timings, refusal/loop rates, native tool success and wall per solved agent task. Avoid accepting a high-percent acceptance from near-zero drafting as a throughput win.
- Proposed composition: quality-preserving per-tensor mixed-bit allocation (GSQ-RCO/ByteShape), custom rotated basis (Gyro), independently trained concise-output behavior (Swift/Signal/ThinkingCap), then workload-aware speculation. These components are **conceptually compatible but have different weights, calibration data, formats and draft coupling**. Need fresh encoder+post-train pack, correct runtime kernels, new held-out KLD and xhigh task tests, no mere file fusion. No verified combined Gyro Signal/Swift GSQ-RCO release in this window.

## Decision and next tests

Keep **Swift1.5 IQ3_S / Strata on RTX5070Ti** as quality-first baseline. New short-context 5070/64GB slow receipt makes exact-owner native262K **fit/admission, tuned-vs-default and no-swap test the next priority**, ahead of quant chasing. Candidate *challenge* matrix: Swift1.5 native IQ3_S vs ByteShape 3.2/3.8 vs base GSQ-RCO vs ThinkingCap27B / Signal27B; separate artifacts/identities and context tiers; compare **time-to-correct-result**, xhigh terminal/tools, long-loop rate, acceptance and quality, not raw TG. Gyro-M/Signal FlashNext is watch-only until native-compatible quant, trusted xhigh results and runtime available.

Mac: stable oMLX and patched staging MTP-OFF, prefix-resume and 2+ agent batch correctness before adaptation. RX6800: original gfx1030 target-only PP parity. Relay: single committed *same-artifact* CUDA->Metal full-state frontier, epoch/lease and async I/O quarantine; no per-token remote decode, no unjustified 40TG/400PP claim.

**No changes to `RESEARCH-TARGETS.md`**, no new strict 128K exact owner physical result, and no product/hardware purchase. Files `RESEARCH-STATE.md` and watch chain only; preserve all code and existing targets.

## Sources (primary)

- https://github.com/Niko1221/Strata/issues/2772
- https://github.com/Niko1221/Strata/pull/2773
- https://github.com/Niko1221/Strata/pull/2761
- https://github.com/Niko1221/Strata/pull/2751
- https://github.com/Niko1221/Strata/issues/2767
- https://github.com/jundot/omlx/issues/4606
- https://github.com/jundot/omlx/issues/4609
- https://github.com/jundot/omlx/issues/4608 (time-anomaly; no promotion)
- https://github.com/jundot/omlx/pull/4613
- https://agention.ai/research/adaptive-speculation/
- https://huggingface.co/agentionai/Qwen3.8-Flash-Next-Gyro-GGUF
- https://huggingface.co/agentionai/Signal-3.8-Flash-Next-GGUF
- https://huggingface.co/agentionai/Signal-3.8-27B-GGUF
- https://github.com/Niko1221/Strata/issues/791 (older calibrated control)

**Next strict watch begins after 2026-10-16 14:10:00 UTC.**
