# Dense Qwen3.8-27B: measured GB10 prefill → M5 Max decode handoff and implications for Project 51 Relay — Nov 9

Source [TensorFold PR#2648](https://github.com/ashhart/TensorFold/pull/2648), created Nov9 04:22:52Z; new strict research cutoff 2026-11-09T18:05:38Z.

## Physical A/B (not owner machines)

Different hardware: GB10 accelerator and M5 Max Mac, ConnectX switched fabric, dense Qwen3.8-27B matching checkpoint, opted-in MKVH2 state handoff. First actual120832-token synthetic prompt TTFT Mac-alone385.3s, handoff136.4s, GB10-alone128.7s. Seven turns through131072 occupied context summed TTFT Mac468.7, handoff208.7, GB10-alone167.8; all replies inclusive598.8/317.7/294.6. 3 scored median blocks; GB10 alone separate later set of runs. Note one +3072-token followup handoff28.4 vs Mac22.4, regressions do exist. Decoder 256-token replies Mac-alone ~13.6–13.8 tok/s, handoff initially20.2 and declines to12.6; mechanism unexplained. 2 concurrent128K sessions stopped by safety headroom threshold, NOT validated.

## Correctness

State transfer ~8.5 GiB at128K, no claim standard network or TB4 bandwidth sufficient. Relative Mac-alone greedy next-token on fixed history differed 0–8/256 for 6 prompts, top-2 logit gaps <=0.25; 1/5 teacher-forced correctness checks still FAILS. A lossless/correct coding-agent Relay cannot be claimed. Exact checkpoint matching does not guarantee exact compute arithmetic due different kernels/backends.

## Portability gates

Owners have RTX5070Ti16GB+64GB DRAM and two independent M1 Max32GPU64, Thunderbolt4 (not ConnectX), main QFN source original GSQ IQ3XXS/3S (sparse recurrent/attention architecture) NOT dense27B. Need prefill state schema including attention K/V, GDN recurrent states, sparse indexer routing and any convolutional/PLE/MTP/draft state, buffer strides, precision/scales, current token count, teacher-forced next-token alignment and long multiagent prefix/restart. An incremental follow-up transfer ~355MB for3072 tokens is a proposed state-layout estimate not physically measured. First research architecture/port design, then HIGH approval before local tests. Compare alternatives PC-alone or two independent M1 workers; quantify total TTFT and wall time for completed tasks, not PP alone.

## Priority

Highest architectural discovery in this window; no change to original GSQ floor or owner expected throughput. Status: third-party physical demo on different setup, open PR, one correctness gate FAIL; adaptation feasibility unknown.
