# Kapitsa × 2021 M1 Max — original QFN GSQ IQ3XXS/IQ3S feasibility (research-only)

## November 6 2026 17:39 EST — latest Kapitsa gates, no source GSQ IQ3_S Flash-Next breakthrough

[Strict watch](./RESEARCH-WATCH-2026-11-06-1739.md) cutoff 2026-11-06T22:39:45Z. No verified merged original GSQ IQ3_XXS/IQ3_S Qwen3.8-Flash-Next-specific expert converter/SSD cache despite older generic IQ3 kernels ([#311](https://github.com/nace-ai/kapitsa/pull/311), specialized Q2-only [#720](https://github.com/nace-ai/kapitsa/pull/720)). IQ3S source ~54.8GB transformer +128K KV~4.1GB or262K~8.1GB before macOS/scratch remains single64GB serious problem; physical M1Ultra128GB source original IQ3S true192K TG34 from old [Splash #47](https://github.com/paperniuk/splash/issues/47) is NOT single32GPU M1Max or262K proof.

[Kapitsa new PR #1024](https://github.com/nace-ai/kapitsa/pull/1024) created18:57Z, `--idle-unload` default auto after10minutes **only when OS memory pressure**; on M5 Pro48GB other dense27B4bit idle footprint ~16GB→34–101MB and internalSSD reload1.7s, no decode change on 3×6 request sets. No source Flash-Next streamed-expert test, no paired 2Mac test (paired engine explicitly never auto unloads), PR OPEN. Its observed compressor 1.05–1.06x and RAM pressure explains why explicit safe OS memory headroom matters, not a way to run whole IQ3S resident. Older [issue947](https://github.com/nace-ai/kapitsa/issues/947) reports M3Max48 Q2 preset reaches budget38.6GB and fails even70 tokens while Splash handles80K; source publishedNov4 **REDISCOVERED older failure**, only comment within new window "ok thanks" not a resolved fix.

Optional fast profile M5Pro48 QFNQ2 from PRIOR watch faster cold prefill7–10% and4/72 flipped top1, keep **precise** for xHigh source QA. 17:39 window had no new original source QFN M1 pass, no physical two M1 TB4 split, no proven IQ3S memory fit. Keep projected estimates low-confidence, targets unmeasured. No owner execution.

## November 6 2026 12:40 EST — fresh fast-mode result and M1 Ultra source comparator

[Watch](./RESEARCH-WATCH-2026-11-06-1240.md) cutoff 2026-11-06T17:40:53Z. Kapitsa optional [fast profile #986](https://github.com/nace-ai/kapitsa/pull/986) merged15:46Z and [M5Pro source Q2 test #1021](https://github.com/nace-ai/kapitsa/pull/1021) new17:32Z: QFN **Q2_0**, 32K precise43.7sec→fast39.5s prefill and64K93.3→87.2s, 64K draft cycle59.4→57.5ms, 32K near tied. Teacher-forced fast changed4 of72 top1 /KL.008845 against precise; **not BF16 source xHigh quality**, heavy64K memory pressure, not user M1 Max. Keep precise default for fidelity. Native generic IQ3_XXS/IQ3_S kernels still not wired to original source QFN specialized Flash-Next GGUF/SSD expert path: no verified new source port.

Useful REDISCOVERED physical [Paperniuk Splash #47](https://github.com/paperniuk/splash/issues/47) originally Nov4 source original GSQ IQ3S on **M1 Ultra48GPU128GB** true192K decode34TG/PP625; **262K startup self-test timed out120sec**. Its 55–64GB measured footprint incl KV on 128GB host does NOT imply safe nearly full64GB M1Max residency. [Splash new M1 fork release](https://github.com/paperniuk/splash/releases/tag/1.6.0-m1) has QFN Q2 one M1Max78.7TG and Flint Q4 on M1Max77TG, but no original source IQ3S M1Max; [#51](https://github.com/paperniuk/splash/issues/51) exact other M1Max 17–32 small-tail hangs must be fixed. One M1 source IQ3S128K remains engineering stretch with correctness-first partial expert storage, not proven full resident. Dual over TB4 unmeasured. No device authorization.

**Snapshot:** November 6, 2026 08:07 EST, cutoff 2026-11-06T13:07:04Z. Main [strict dated watch](./RESEARCH-WATCH-2026-11-06-0807.md). **No hardware execution or permission for model downloads/CI/builds.**

## 1. Baseline and what is ACTUALLY implemented

Owner two separate 2021 M1Max32GPU/64GB Macs. Proven Paperniuk DS4 **original GSQ IQ3_XXS** at *occupied*128K=278PP/34.2TG and259K=258PP/31.7TG. Original GSQ IQ3_S desired, not established fast fully resident on one64GB at128/262K. Original ISTA official [source model card](https://huggingface.co/ISTA-DASLab/Qwen3.8-Flash-Next-GSQ-RCO-GGUF): IQ3XXS first shard47.0GB + SSD PLE28.8GB; IQ3S first shard54.8GB + SSD PLE28.8GB, source PLE IQ4_NL memory-map rather than full 28.8GB pin.

Kapitsa [docs](https://github.com/nace-ai/kapitsa/blob/main/docs/usage.md) already supports generic qwen35/moe and Flint GGUF IQ3S expert kernels; [#311](https://github.com/nace-ai/kapitsa/pull/311) adds tested **IQ3XXS IQ1S native Metal** code for *different model architecture*, initially Qwen import IQ3XXS opt-in KAPITSA_IMPORT_IQ_NEW=1. **Flash-Next specialized** GGUF Q2_0 conversion [#720](https://github.com/nace-ai/kapitsa/pull/720) REFUSES non-Q2_0 routed-expert weights such as original GSQ IQ3S/XXS; streaming expert store only has Q2_0 slot repack/layout, and distributed pipeline path not general precision magically. No native original-GSQ Flash-Next success just because an IQ kernel file exists.

Source [Kapitsa v0.2.31](https://github.com/nace-ai/kapitsa/releases/tag/v0.2.31) recent, source cross Mac same-quant comparison Q2_0 M5Pro vs Splash near decode tie; M1Pro generic IQ kernels and M1Ultra other quant throughput never prove M1Max Flash-Next GSQ speed.

## 2. Honest memory admission accounting

| Approximate decimal GB | Single GSQ IQ3_XXS | Single GSQ IQ3_S |
|---|---:|---:|
| Source transformer first shard | 47.0 | 54.8 |
| Source PLE shard / SSD backed | 28.8 disk | 28.8 disk |
| Approx QFN KV at ACTUAL 128K | 4.1 | 4.1 |
| Approx QFN KV at ACTUAL 262K | 8.1 | 8.1 |
| 128K model+KV floor, before EVERYTHING else | 51.1 | **58.9** |
| 262K model+KV floor, before EVERYTHING else | 55.1 | **62.9** |

No OS memory, mapped-PLE hot page cache, MTP/draft, sparse-attn/GDN state, dispatch scratch, Metal residency, speculative branches, memory fragmentation, concurrent tools/agent processes or vision in those sums. **Kapitsa documented default 64GB Mac working budget about 44.0–51.5GB**. Physical unified memory is not safe usable Metal memory at 100% allocation. Consequently neither original XXS nor IQ3S is trivially fully resident with long KV under Kapitsa defaults. Source DS4 XXS long physical success is proof for DS4, **not Kapitsa format/memory admission**.

- IQ3XXS128/259K: proven in DS4; Kapitsa port could achieve original quality but must show correct QFN loading, KV and memory.
- IQ3S128K: plausible single-M1 *stretch* with selective SSD expert cache or very aggressive safe memory budgeting; generally **not fully resident at normal Kapitsa budget**.
- IQ3S262K: 62.9GB floor before OS means **substantial experts offload, lower KV precision, or other reduction necessary**; no established stable throughput.
- Split over two 64GB Macs can avoid all-experts-on-one memory, but requires source-compatible pipeline and TB4 actual latency and correct GDN/QSA/PLE/MTP/agent state. Separately address two independent concurrently used workers vs a pipelined single model.

[Kapitsa #993](https://github.com/nace-ai/kapitsa/pull/993) only lifts conservative partial expert RAM-share cap for >=120GB RAM />=60GPU cores, EXCLUDES both owner32GPU64GB M1Max. [#991](https://github.com/nace-ai/kapitsa/pull/991) M1Ultra +42% 35B prompt throughput does not give M1Max bonus because Max already has the larger chunk default; no QFN inference. [#986](https://github.com/nace-ai/kapitsa/pull/986) fast-mode reduces numerical precision compared to exact precise path; not a quality proof.

## 3. Research-only port sequence (PROPOSED, not APPROVED)

1. Verify source GGUF first-shard tensor inventory, original codebook layouts and correct source PLE IQ4NL mapped rows against independent GGUF dequant; do not transform source IQ3S into different 4bit unless separately disclosed as new quant.
2. Integrate already-existing IQ3S/XXS native MoE block kernels into Flash-Next routed expert and cache slot family, preserving all special Qwen3.8 hyperconnections, GDN, QSA, MTP, PLE. Distinguish source GGUF tensor blocks from converted affine representation.
3. Introduce correct per-tensor memory admission and partial expert-store sizing; guard macOS safe OS/wired footprint, swap, expert miss rates, correct KV precision; no unsafe RAM cap override.
4. CPU oracle BF16/source GGUF parity checks for every block type, target logits and MTP verification under explicit thinking settings, exact tools/response JSON and executed heldout coding tasks, 128K and262K **actually occupied** (not merely --max-context).
5. Only after HIGH, controlled one-M1 physical A/B against Paperniuk DS4 original GSQ XXS at cold and warm turns (PP/TG, TTFT, idle GPU/ANE startup, swapping, SSD reads, quality); then high-quality IQ3S and actual TB4 split if supported.
6. Continue model & quant radar separately. Unsloth Dynamic3.1 similar-sized mixed quant is an **unproven** alternative; never silently replace pristine GSQ floor.

## 4. Forecast status

Prior assistant's proposed single-M1 IQ3S128K **200–290 PP/24–33TG with nearly resident** and partial-stream 100–250PP/10–28TG were **speculative engineering guesses**, neither published Kapitsa physical measurements nor stable supported format. Mark **LOW CONFIDENCE**, do not promote to numerical targets. Actual Paperniuk DS4 source XXS values and 2021 M1 Max identity are the only firm performance anchor.

**Next evidence:** merged Flash-Next source IQ kernels + live actual M1Max memory, detailed KV and source quality parity, not a newer-Mac Q2 headline.
