# Project 51 research watch — November 15, 2026, ~09:32 EST
**Previous verified strict cutoff:** 2026-11-15T14:23:03Z. **New cutoff:** 2026-11-15T14:32:00Z (user request available only to minute; seconds NOT independently verified). This is a **thematic deep-discovery review of historical rumors**, not a claim that old sources are fresh between these two cutoffs. No newly verified Qwen4-Flash weight release during this small interval.
[Full specialized Qwen4 sizes and Flash forensics](./QWEN4-SIZE-RUMOR-FORENSICS-2026-11-15.md).

## A. Verified vs rumored
- OFFICIAL [Alibaba Sep22](https://www.alibabacloud.com/en/press-room/alibaba-unveils-roadmap-on-full-stack-ai-strategy): Qwen4 in training; **5–10T planned scale belongs to Qwen4.5/Qwen5** flagship roadmap, NOT Qwen4-Flash.
- OFFICIAL [Qwen Flash-Next card](https://huggingface.co/Qwen/Qwen3.8-Flash-Next): architecture preview, **125B backbone, 6B active + 51B ngram +4B MTP**; no confirmation that Qwen4-Flash shares size or source checkpoint.
- REPORTED Oct29 Apsara slide names Qwen4-Max, Plus, Flash, 27B. No parameters other than “27B” tier name; “Nov2–8” spoken launch rumor failed as whole-family release.
- OFFICIAL [QwenCloud](https://docs.qwencloud.com/changelog/models): Nov11 `qwen4-max-preview` API through Token Plan; 1M context, params undisclosed; ends Nov25. No available genuine Qwen4-Flash/27B open weights found.
- VERY WEAK 35B-A3B leak is secondhand A3B tester with **NO total size**; “35B” guessed from earlier generation, not reported Apsara tier.
- REDISCOVERED [Whittle 35B-A3B](https://huggingface.co/whittleOrg/Whittle-Qwen-3.8-35B-A3B): genuine **third-party** research checkpoint in same `qwen4_exp` architecture, 25B main+10B table,3B active, Q4_K_M21.3GB, incomplete distillation; proves feasibility, not Qwen product plans.
- [Qwen qwen-code PR#15762](https://github.com/QwenLM/qwen-code/pull/15762) and [#15987](https://github.com/QwenLM/qwen-code/pull/15987) are client wildcard/defaults/tests on **FAKE endpoint**. Qwen4.5-Max/coder-plus/omni-120b-think IDs are not confirmed sizes or real checkpoints. Third-party XPU Qwen4-27B kernel primary PR22 now 404/private; no weights or official config, cannot verify spec.
- HF third-party “Qwen4-27B-GGUF” [Chungulus](https://huggingface.co/Chungulus/Qwen4-27B-GGUF) and [InterpreticAI](https://huggingface.co/InterpreticAI/Qwen4-27B-Uncensored-v3) explicitly are placeholders **without weights**. November16/18 dates are community countdown forecasts, not Alibaba announcement.

## B. Owner hardware / forecast consequences
If Flash remains125B+51B, owner originalGSQXXS 2021 M1Max64 historical true128K PP278/TG34.2,259K PP258/TG31.7 near57GiB memory is relevant **only as an old-model, old-quant, measured baseline**; not a Qwen4 speed forecast. 4bit raw on180B ~90GB weights before overhead, cannot fit as all-resident Q4 one Mac. New 35B-A3B could fit Q4/Q5 on each64GB but has no source-backed Qwen4 release evidence; dense27B could fit Q5. Larger Flash may require expert/PLE streaming or cross-Mac partition. Two 64GB Macs remain independent and Relay CUDA→Metal full QSA/GDN/PLE state is unproven.
Keep frozen PC original GSQ IQ3S, true32K INT8KV one slot spec1 NO DRAFT and full code tool parity; no action on owner hardware.
**NEXT STRICT CUTOFF 2026-11-15T14:32:00Z (minute-resolution).**
