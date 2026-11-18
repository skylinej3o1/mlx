# Project 51 — ranked discovery scratchpad (refreshed 2026-11-18 02:51 EST)

Strict source watch [RESEARCH-WATCH-2026-11-18-0251.md](./RESEARCH-WATCH-2026-11-18-0251.md), cutoff 2026-11-18T07:51:25Z. Owner hardware: two distinct M1Max64, original GSQXXS, RTX5070Ti16/host64 frozen GSQIQ3S v2 32K spec1 NO DRAFT, RX6800 nonXT16VRAM/host16. No source model changes authorized. Scoring F,N,E,A,I each 0–3; total 3F+2N+3E+2A+I max33; evidence triage only.

## Ranked active leads (maximum 12)
1. **Tool-order / HaikuSwarm correctness — 28/33 (F2,N3,E3,A3,I1).** [TensorFold #3775](https://github.com/ashhart/TensorFold/issues/3775) concrete parallel same-function reverse-arrival result-ID bug and local fix; check merged remedy and cross-engine AB/BA replay, include rendered positional template hashes. Security/correctness priority.
2. **Native oMLX CUDA ↔ source GSQ bridge — 25/33 (F3,N2,E2,A3,I0).** [0.8.0](https://github.com/jundot/omlx/releases/tag/v0.8.0), [#5396](https://github.com/jundot/omlx/pull/5396), [SSD PLE #5384](https://github.com/jundot/omlx/pull/5384). Investigate whether any original GSQ GGUF state is consumed through helper rather than native oQh model; check capacity of one M1Max64 and per-layer resident QSA/GDN/PLE.
3. **First PC Basalt original IQ3S plan — 25/33 (F3,N2,E2,A3,I0).** [#415](https://github.com/jesdga95/basalt/pull/415) QAD work not same model; [#412](https://github.com/jesdga95/basalt/pull/412) other 112GiB host drafted5070Ti; preserve original pack, 32K spec1, INT8KV, CPU double and task checks; no execution without HIGH.
4. **Dense27B oQh vs full task success — 25/33 (F2,N3,E3,A2,I0).** [#5317](https://github.com/jundot/omlx/pull/5317) merged: same 12.2/15.2GiB Qwen27B with KL improvements; compare exact task/tool workflows to prior GPTQ4/Unsloth, not just token-level KL.
5. **GDN convolution helper buffer — 22/33 (F1,N3,E3,A2,I0).** [#5396](https://github.com/jundot/omlx/pull/5396) open: M3Ultra/4090 27B 0.66GiB memory benefit, 49-layer and TTFT uses separate local packing patch. Demand merged independent QFN/5070Ti measured transfer.
6. **Paperniuk original GSQ M1 quant scope — 20/33 (F3,N1,E1,A3,I0).** [#70](https://github.com/paperniuk/splash/pull/70) dense MLX4 kernel gains but IQ3_XXS output slowdown and changed greedy. Source GSQ 128/259K and idle/SSD spill check only after explicit HIGH.
7. **Qwen4 Flash real configuration — 20/33 (F3,N1,E1,A3,I0).** Official Qwen model card, tensor index, active/total, PLE/MTP, date and license missing. No extrapolated Chinese/community rumor promotion.
8. **Agent cache/SSD admission — 20/33 (F2,N2,E2,A2,I0).** [Strata #5697](https://github.com/Niko1221/Strata/issues/5697) glibc heap retained memory, [#5895](https://github.com/Niko1221/Strata/issues/5895) 260K main re-read when short classifier interleaves; rendered prompt provenance and physical RAM gates.
9. **oMLX concurrency exactness — 19/33 (F1,N2,E2,A3,I0).** 0.8 release scheduler and [#5392](https://github.com/jundot/omlx/pull/5392) Hot-only VLM cache not truly hot; task-level correctness and immutable vision provenance.
10. **Strata route warm correctness — 19/33 (F2,N2,E2,A2,I0).** [#6171](https://github.com/Niko1221/Strata/issues/6171) earlier early-EOS with warm route prior, needs independent owner quant and completion checks.
11. **Two-Mac distribution residency — 16/33 (F2,N2,E1,A2,I0).** Each original GSQ 259K ~57GiB, TB4, no shared RAM; multiagent separate decode more plausible until demonstrated native split.
12. **Basalt loader/time controls — 13/33 (F1,N1,E2,A1,I0).** [#411](https://github.com/jesdga95/basalt/issues/411) two independent other-hardware A/B no speedup; preserve measured end-to-end, not marketing.

## Deprioritized/closed (up to 8)
- [Basalt0.4.1 release](https://github.com/jesdga95/basalt/releases/tag/v0.4.1) published Nov16 16:09Z: earlier "no release" was mistaken, REDISCOVERED historical correction, no first-plan change.
- Qwen4 224B/552B competitor analogy and ~125B backbone preference: no first-party Flash size, keep as prior speculation.
- oQh source QFN 70.8GiB+ on one M1Max64: above residency, not GSQ replacement.
- 2×V100 NVLink [Strata#6023](https://github.com/Niko1221/Strata/pull/6023) not owner TB4 or CUDA/Metal.
- RTXPro4500 Blackwell host499GiB [Basalt#417](https://github.com/jesdga95/basalt/pull/417) benchmark not RTX5070Ti/host64.
- Kapitsa M5/M6 release speed no old M1 source gain.
- Basalt QAD PPL drop conflicting BF16 KL rise: quality not proven.
- Paperniuk PR70 no GGUF IQ3_XXS gain in latest evidence.

## Next exploration turn
1. Original-source GSQ Qwen4/Flash manifest + precise Chinese-primary claimed leak provenance, not recycled screenshots.
2. QFN tool-result positional template consistency, patch upstream state and cross-runtime benchmark fixture from #3775.
3. oMLX 0.8.0 + #5396 review: original GGUF/Splash bridge, 5070Ti16 layer budget and old M1 residency, without downloads/runs.

## Source map growth and discovery debt
New primary sources: official oMLX0.8.0 release, merged oQe/oQh/helper, #5396 GDN slice, TensorFold#3775 and Kapitsa0.2.37; independent Basalt loader A/B. Discovery debt: official Qwen4 Flash configs; true source GSQ GGUF bridge; unchanged tool-call identity after chat template tokenization; old M1 long-uptime cache/SSD spill; comparable real agent-coding tests; reliable 5070Ti16+host64 Basalt source IQ3S no-draft physical32K. Only docs research, hardware HIGH.