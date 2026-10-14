# Project 51 research watch — 2026-10-14 16:44 EDT

**Previous strict cutoff:** 2026-10-14 17:52:46 UTC (the 13:52 EDT watch already on the branch; this supersedes the user's older October 13 handoff).
**New strict cutoff:** 2026-10-14 20:44:16 UTC.
**Method:** GitHub connector direct REST inspection of issues, PR bodies, comments, statuses and timestamped commits across Strata, oMLX, mlx-serve, Basalt, Strata-for-Mac, Sushi, llama.cpp, vLLM, SGLang, pi-vcc, adaptive-KV fork and DS4; supplemental targeted public searches. Mark new reports created *after* the prior cutoff separately from updates to older reports, and from recovered older evidence. No user-hardware run was performed. Open PR is not merged production behavior.

## Executive decision

**No planning target movement and no certified verifier modification.** Still no physical dual-M1 Max 64GB Flash-Next PP2/TB4 sustained B1 TG at filled ~128K, no exact M1 DASLABS Swift1.5 IQ3_S 128K/262K, and no exact owner RTX5070Ti16/64GB Swift IQ3_S filled 262K xhigh result. More attractive *tests* emerge for Apple file-backed MoE weights, long-context speculation selection, and 2–5 Pi agents. Main production risks remain fit/retention, checkpoint identity, numerical state, and multi-agent isolation. Preserve Strata v0.1.42 control vs 0.1.44.1 candidate vs Basalt/Linux; no GPU purchase.

## NEW (created after previous cutoff) — high-value

### oMLX #4541: mapped / read-only file-backed model weights; OPEN, not deployed upstream

https://github.com/jundot/omlx/pull/4541 (created Oct14 19:23 UTC).
Proposes opt-in safetensors mmap -> MLX zero-copy DLPack tensors, pages reclaimable under memory pressure, with tensor-alignment enforcement/realignment and a conservative resident-sample admission guard. A **M2 Max 32GB, macOS 27** 22GB Ornith 35B-A3B oQ4e report shows process phys_footprint ~23GB -> ~2.0–2.6GB, load 12.6–13.2s -> 2.2–2.3s; warm short-context decode 69–80 -> 65–66 TG; first postload prefill **540–1000 -> 143 PP** because weights fault in from SSD; 19.6K requests 1/4 -> 4/4 completed, but slower/variable. For a separate dense 9B, footprint 8.2->1.5GB and warm decode ~46–48 unchanged. **These are model/process/OS-specific observations; file-backed pages still consume real physical RAM while resident, may incur SSD faults, and mapped weights skip gate/up fusion.** Metal wired ceiling remains binding: PR explicitly does NOT enable a model larger than `iogpu.wired_limit_mb`. Different from a measured full DASLABS Flash/Swift model and not a 64GB M1 fit guarantee. Trial only in isolated branch with load, cold/warm, paging, chunk, memory-pressure, KV and 3-agent telemetry. Do not modify any model files without explicit backup/realign approval.

### mlx-serve #853: long-context dense 27B *MTP beats DFlash2*; NEW OPEN ISSUE

https://github.com/ddalcu/mlx-serve/issues/853 (Oct14 20:24 UTC).
**Actual 128,000-token document prefill** on M4 Max 128GB, mlx-serve 26.10.2, Qwen3.8-27B MLX-Serve 4bit/8bit, 2 runs per task arm, greedy 320-token prose/code/recall warm suffix:
- 4bit DFlash default: 9.9/18.1/11.6 TG; `--no-drafter` MTP: **19.1/26.0/23.5**; no-drafter/no-MTP PLD 15.5/15.1/14.7.
- 8bit default 6.8/13.0/10.6; MTP: **13.2/22.2/16.3**; PLD: 11.1/10.4/10.5.
- Approx 172 PP cold across modes; short context 8bit DFlash 104 TG for code at 2K (different regime).
This is a **strong A/B priority for each M1 dense-27B lane**, not an M1 TG forecast, Flash-Next claim, or physical long-context capacity on 64GB. Compare no drafter, MTP, DFlash with filled 16/64/128K and full solved-agent-wall time.

### mlx-serve #852: scheduler premature DFlash yield; NEW OPEN PR

https://github.com/ddalcu/mlx-serve/issues/852 (Oct14 20:16 UTC; issue text reports implementation/bench; verify integration before use).
On **M5 Ultra** Qwen3.8-27B 4bit+DFlash2, 400-output-token synthetic concurrent requests, 2–5 streams previously caused the DFlash slot to run plain beside MTP batch. Holding draft until the competing cohort meets MTP crowd threshold changes aggregate 2 streams 57.0->123.7 TG, 3 83.1->170.6, 4 107.8->213.3, 5 129.0->250.3 (six runs/cell). 1 and 6–8 unchanged; earlier never-yield alternative regressed 6–8. **No filled-context disclosure, no M1, no interactive Pi success-rate benchmark**. Candidate for adaptive per-lane 3–5-agent dispatch, not a direct two-M1 expected rate.

### Strata #2482: actual 352K filled-context CUDA receipt; NEW ISSUE, different hardware/quant

https://github.com/Niko1221/Strata/issues/2482 (Oct14 19:34 UTC).
**RTX5080 16GB + 128GB host**, original v0.1.44, Unsloth **UD-IQ4_XS (not DASLABS IQ3_S, not Swift)**, Q8/int8 KV, MTP; 109-message real conversation **352,130 tokens prefilled** (max context configured 786,432; that is NOT the filled count). `STRATA_ROUTE_TAIL_SKIP=7` warm decode ~60.0 vs 56.5 TG, +6.2% over small 3-vs-2 run sample, cold PP ~2272–2284 unaffected, cold decode inconclusive. Separate nonpaired real chats reach ~200–266K; anecdotal quality tests do not certify quant/answer parity. Router cache hit rate changes denominator by excluding skipped experts. **No transfer to owner 64GB host, RTX5070Ti, or Swift.** New experiment: log omitted-route denominator and exact task-logit/quality A/B before accepting +6% inference.

### oMLX #4540 and #4539: MTP snapshot and reasoning-budget compatibility; OPEN

https://github.com/jundot/omlx/pull/4540 (Oct14 19:02 UTC): pooled `PoolingCache.offset` is rows but target is tokens, and prefix snapshots were captured too late after an activation seam. Fix records C-1 boundary before advancement. 83 focused and 17,092 full tests pass in reported environment. **Estimated** 4.4–4.7GiB pooled head copied at 128K plus read/write overhead (not timed); applies directly to GLM5-style pooled MTP; do not call it a Flash/M1 TG win. Preserve full draft state and exact token-position units on Relay export.
https://github.com/jundot/omlx/pull/4539 (Oct14 17:52:53 UTC): Qwen3.6 thinking-budget closer selected bare historical `</think>` rather than generation `\n</think>\n\n`; forced budget leaked reasoning into `content` (thousands more tokens); corrected resolver tested real Qwen3.6 and passes suite. Qwen3.8-27B templates already use wrapped close in reported test; no demonstrated exact Swift issue. Check Pi reasoning/content boundary under real budget, avoid believing speed from malformed parser output.

### Other NEW source changes worth tracking

- vLLM https://github.com/vllm-project/vllm/pull/61670 (created Oct14 17:53) enables graph-safe in-place fused MTP sparse-MLA metadata update when DCP=1; single CUDA-related focused test, **no bench, no CUDA->Metal transfer, not merged**.
- Strata https://github.com/Niko1221/Strata/pull/2492 (Oct14 20:23): RDNA4/gfx1201 full-die wave-grid stall avoided with empty workgroups; R9700 model 32K 59–60->~60.5–61.4 TG and 71–72.6->~73.9–74.8 TG; HIP full-die RDNA4 **not RX6800 gfx1030**. Open.
- pi-vcc https://github.com/sting8k/pi-vcc/issues/53 (Oct14 18:17): use host Pi `getAgentDir()` rather than `~/.pi/agent`; portability improvement, no inference/memory enhancement.
- Basalt Oct14 commits https://github.com/jesdga95/basalt/commit/4a9e10f5dd41b87d388fe45fe2142fc74b62a601 and https://github.com/jesdga95/basalt/commit/b4c63b55754637f4c72ad53a0f791d425f71eb36 warn **self-converted packs are slower than official ones**. No quantitative A/B in these commits; pin identical packing and official-vs-converted provenance in Linux Strata/Basalt comparison.
- New quant work (e.g. vLLM compressed-tensors MXFP6 PR #61666) is unrelated accelerator format, not a measured source-quality DASLABS IQ3_S, Swift1.5 3_S, Byteshape 3.84 or Apple Metal replacement. **No validated new target quant/variant in the strict window.**

## UPDATE (older issue / older merged feature, new information after cutoff)

### RX6800-related gfx1030 persistent HC verifier needs fail-loud timeout

https://github.com/Niko1221/Strata/pull/2226 (created Oct13, updated Oct14 20:12; **OPEN**). Two RX6900 XT gfx1030 layer split, HIP 10, `STRATA_HC_PERSIST=1` hyper-connection read speed 1.35–2.10x microkernel; newer alternated end-to-end verify-window A/B on revised branch 4K -2.7%, 32K -6.1%, no prompt change. **Earlier PR had critical silent corruption:** a timed-out persistent barrier returned partial outputs and poisoned subsequent windows. New commit `26649c6c` adds nonfinite signal/abort, resets barrier, counts+logs abort; gfx12 disables unsupported timeout path. Focused injected-fault 3-window recovery passed, no runtime timeout in measured runs. Proposed *candidate* for user's RX6800 **only after exact single-card gfx1030 parity and forced-timeout tests**; this is not a proved RX6800 or Relay performance delta.

### Clean Strata Foresight swap fix validated on 0.1.44 (not a new fix)

https://github.com/Niko1221/Strata/issues/2134 — Oct14 19:44 third-party rerun **clean v0.1.44**, Flash IQ3_XXS RTX PRO6000 with capped cache: HumanEval 50 ×3, 606,647 + 974,771 + 1,451,520 = **3,032,938 checked slots, 0 BAD**, versus v0.1.43 19 BAD in 425,973. Dropped/exchange invalidation confirmed in log. Encouraging for v0.1.44.1, but opt-in Foresight remains behind own RTX5070Ti/64GB nonce, timing, and quality gate. Additional RTX4080S 16GB+64GB DDR4 reported ~57.4 TG for ~30K output-token task IQ3_XXS **not** IQ3_S 262K filled.

### Official Strata Metal 0.1.44.1 repaired a serious earlier M2 GDN kernel bug, small-Mac arena still problematic

https://github.com/Niko1221/Strata/issues/2323. Original 0.1.44 M2 Max multi-token GDN kernel requested 512 threads but Metal pipeline only allowed 448, silently left stale GDN states and garbage outputs. **0.1.44.1 already fixed this before the previous cutoff**, and Oct14 comments confirm M2 Max parity on older SDK. NEW Oct14 19:15 comment from M2 32GB still reports `metal prompt: no arena region for the prompt buffers` (previous 24GB repro); do **not** mislabel GDN corruption as still present in 0.1.44.1. Still no owner M1 Max 64GB IQ3_S / Swift production-level admission result.

### Additional correctness / benchmark warnings from earlier-opened items

- llama.cpp https://github.com/ggml-org/llama.cpp/pull/30541 (opened Oct14 17:44, updated 20:02, OPEN): on-device quantized-KV state transfer `size / element_size` copied **blocks not elements**, only 1/32 of Q8_0/Q4_0 buffer; save, restore, differently chunked copy all fixed in PR; CPU/OpenCL tests pass. **Critical Relay test design for quantized KV**; not CUDA/M1 end-to-end evidence.
- SGLang https://github.com/sgl-project/sglang/pull/44140 (Oct13 origin, Oct14 update; OPEN): PD DSA indexer export incorrectly transmits cached prefix's indexer pages before L2/L3 restore or rewrites shared L1 pages; proposed transfer of suffix pages only past committed `decode_prefix_len`. Tested GLM5.3 NVFP4 real deployment per author, no quantified speed. Relay must serialize/own cached QSA-indexer prefix as part of committed frontier.
- vLLM https://github.com/vllm-project/vllm/issues/61658 (created Oct14 16:44 before boundary, updated after): shared-secondary-tier cached “absent” lookup can remain stale while other process writes block; CPU/two-process repro, no fix yet. Add multi-agent negative-cache version/invalidation/TTL gate for shared disk/root cache.
- Strata https://github.com/Niko1221/Strata/issues/2418 (created earlier Oct14): 2x3090 asymmetric x16/x4 no-P2P Qwen Flash IQ3_S layer split auto 0.1.44.1 still regressed vs 0.1.40.3; code TG ~148->135, 90K PP ~3416->~3097–3144 despite 10K improvement, split K selection changed. Does not quantify TB4/M1.
- Strata https://github.com/Niko1221/Strata/issues/2456 (created at 15:25 before cutoff; updated later): 3D app-building Claude Code harness scores mean 86 (n9) for original IQ3_S, ~90 (n4–5) for UD IQ4_XS/Q4_K_XL, ~80 (n3) Swift IQ3_XXS, on RTX5060Ti16/96GB. **Not controlled checkpoint/quant/runtime equivalence**, different token costs and subjective game scoring; cannot claim DASLABS 3_S Q5-equivalent or Swift degraded from these means. Use for paired target-quality evaluation design only.
- Sushi https://github.com/beamivalice/sushi/issues/44 (created Oct12, updated Oct14): real **M1 Max 64GB** Sushi-2.6bpw owner says 25–30 TG; supplied log processes **11,855 prompt + 497 completion**, despite configured `ctx-size 248000`; measured line shows 25 TG, 251 PP with 10,466 tokens cached. **Not filled 248K**, different quant, not DASLABS IQ3_S.
- Recovered older mlx-serve https://github.com/ddalcu/mlx-serve/pull/815 **merged Oct12**, Qwen Flash-Next GDN f32 recurrent state and decay gate correct earlier bf16 rounding, 206/1728 heads nondecaying; author M5 Max reports teacher-forced PPL reduction on a branch 56.95->39.76 decode, 48.16->42.35 prefill, same model numerics. **Already merged before this watch; do not label new.** Strong reason to gate GDN f32 state and long-horizon quality on Mac comparison.
- mlx-serve 26.10.2 Homebrew `libmlx.dylib` rpath failure https://github.com/ddalcu/mlx-serve/issues/838 (older issue with new update): packaging/startup regression; source/binary baseline and installation route are benchmark identity.

## KNOWN / no changes to existing prior watch

Oct14 13:52 watch already covers **vLLM #59790** remote writes surviving abort, **vLLM #61032** NIXL 1.5 strided KV region descriptors, **llama.cpp #29107** Intel SYCL IQ3 reorder, **SGLang #42818** cache adapter namespace, and Oct14 earlier oMLX #4508 batched DFlash / #4509 SSD requeue and Strata official v0.1.44.1. Their performance or correctness is **not counted again as newly landed** here.

No new branch commits in selected post-cutoff default-head checks for Niko1221/Strata, jundot/omlx, Sushi, Strata-for-Mac, mlx-serve, pi-vcc, adaptive KV fork or DS4; **OPEN PRs and issue updates do not mean release availability**. Basalt alone has two new docs/conversion-warning commits among those exact repos. llama.cpp post-cutoff merges are OpenCL/packaging metadata and SGLang default-branch housekeeping, no exact-project TPU/CUDA/Metal decode rate. Broader PR listings were screened for relevant quant, sparse indexing, state transfer, memory and concurrency; absence of identified exact target evidence is not a claim of exhaustive GitHub coverage.

## Next execution-gated fleet plan

1. **Lenovo RTX5070Ti 16GB / 64GB**: fix artifact identity first; v0.1.42 vs 0.1.44.1 vs Basalt official/custom packing, Linux, same Swift IQ3_S or separate explicit quant cohorts. Filled 16/64/128/192/~262K, cold PP, TG/TTFT, host pinned bytes/VRAM free/page faults, full vs quantized KV, MTP on/off, Foresight off then stress, parser/tool/xhigh solve wall, 2-agent private nonces. No `max_context` without observed filled count.
2. **Two M1 Max64GB Macs**: maintain independent oMLX/Sushi-like source-identified agent lanes, dense27B baseline, MTP vs DFlash at 16/64/128K; optional isolated mapped-weight trial on realigned copy if it fits within wired cap and quality. For original DASLABS IQ3_S official Strata Metal: memory/admission + GDN parity + 32K/128K smoke before any 262K claim; no Mac Swift support assumed. Dual PP2/TB4 remains engineering research, not fleet production.
3. **Relay CUDA->Metal**: first *one-shot cold-prefill ownership handoff*, NOT per-token network TP. Identity must include exact checkpoint/tokenizer/quant/layout/GDN+conv+QSA/indexer+KV states, EOS/tool replay, confirmed token frontier, typed block lengths, model/adapter namespace, transfer epoch, writer/reader drain. Add quantized KV 1/32 copy-size regression, stale-negative-tier probe, MTP pooled offset regression, prefix/suffix indexer overwrite detection, and crash/abort/timeout/restart multi-agent tests.
4. **RX6800 gfx1030**: bring up full HIP Strata/ROCm with normal server measurements and ROCm FP16 prompt GEMMs, baseline speculation OFF. Only then opt-in `STRATA_HC_PERSIST` fail-loud abort / parity tests with exact RX6800; RDNA4 grid_pad and Intel SYCL chunked pinning are not its kernels.
5. **Quants and quality**: source-like Swift IQ3_S remains aspirational if no independently verified exact pack. Hold custom compact 3.3–3.6bpw/xhigh vs oQ5e comparator, paired prompt/task quality, record tool success, reasoning token cost, and correct output, not just speed, and avoid unsupported Q5/Q6-equivalence rhetoric.

**RESEARCH-TARGETS.md unchanged; certified P58/P61/P69B3/P69B6/P69B11/P69B12 verifier and source-code targets untouched.**
**NEW STRICT HARD RESEARCH BOUNDARY: 2026-10-14 20:44:16 UTC.**
