# Latest external runtime watch

## Read order for every new research pass

1. Read the durable canonical state first:

   `experiments/p51-q8-verifier/RESEARCH-STATE.md`

2. Then read the newest dated delta:

   `experiments/p51-q8-verifier/RESEARCH-WATCH-2026-09-01-2030.md`

3. If reconstructing history or validating whether a source is genuinely new, scan all
   dated `RESEARCH-WATCH-*` files newer than the canonical state's consolidation point.

4. Also read the focused kernel-mining note when looking for portable optimization ideas:

   `experiments/p51-q8-verifier/RESEARCH-MINING-2026-09-01-IQ-PANEL.md`

## Why this pointer changed

The previous version of this file was stale at the 2026-09-01 Early-Evening watch even
though Post-Early-Evening and Night deltas already existed. In addition, the Night pass
rediscovered DS4 issue #607 as though it were new even though that exact dual-M1 report
had already been found and used in the project on 2026-08-01; it had simply fallen out of
the later formal watch-note chain.

`RESEARCH-STATE.md` now carries durable architecture/runtime anchors forward so a dated
note cannot silently erase project knowledge.

## Current newest delta — 2026-09-01 20:30 ET

The latest pass records:

- correction: DS4 #607 is a historical known dual-M1 anchor, not a new discovery;
- llama.cpp #28213: gathered selected-K/V QSA decode, with reported +6% at 31K,
  +19% at 62K, and +50% at 130K on dual A6000;
- oMLX #3320: long-context wide-MTP/direct-QSA evidence now requires technical
  requalification after a low-margin parity failure;
- oMLX #3364/#3365: Qwen3.8-27B ANE long-prefill admission/escalation repair;
- DS4 #922 rechecked: still no sustained 0731 dual-M1 decode TG;
- Layr exact 27B frontier still `3.7291100105909`, #1481 newest visible submission;
- updated B1, long-context B1, and B2-B4 aggregate confidence ladders.

External evidence does **not** modify the certified P69 checkpoint.
Consult `CURRENT.md` for verifier state; P69B13 remains next using existing profiling data
only.
