# M1 Inkling, long context, original GSQ analogue and NariQ — Nov25 03:40 EST

[Full watch](./RESEARCH-WATCH-2026-11-25-0340.md) includes provenance and exact cutoffs. 
- Apple7/8 [#95](https://github.com/paperniuk/splash/pull/95) native M1Max32 paired weights/draft MLX4 geo57.5→73.1TG, code69.8→90.5,7.2K document32→52.9; UDQ4KM geo57.1→68.5 and code74.7→87.6. Open; no full agent quality or 128/259K. #86 updated to upstream1.7.3 port; actual M1Pro14 32GB older port test shows batch4 works but Qwen3.6-35B faster. 
- oMLX #5624 exact M1Max64 attention bottleneck at32K 7.9/29ms, proposed ~13% step time gain unmeasured. #5631 window state turn ends M4Pro64 69-turn mean TTFT10.3→2.8s and #5628 GDN N4 estimated half storage on QFN, live only 2B. Splash1.7.3 long-session tail fix shipped on upstream, not M1 fork. 
- Basalt #696 original GSQ IQ3S self-converted on 5060Ti16/270K/62GiB Linux PP1078/1601@16/64K TG152.4 benchmark; mixed UD draft/MTP and different pack, not frozen trial. #705 Linux CUDA registration improves PP with other quant/hardware. #675 4bit KV saves memory but loses acceptance/decode speed. 
- NariQ #5 CUDA 5060Ti pp8192 675→1424, #6 RDNA4 8.95→25.74TG, no M1 or gfx1030. #332 PolyStrata target RDNA2 dot4 has only RDNA3 proxy data; actual Strata RX6800XT #7108 failure caution. 
- Keep original quality floor and all owner benchmarks unrun. Independent older hybrid cache translation paper is conceptual Relay lead only. 
