P42R5 ROBUSTNESS RESULT
=======================

Architecture:
  Q5/G32 full-vocab search
  -> deterministic hierarchical Metal top-4
  -> gathered Q6/G32 four-row scoring
  -> highest Q6 score
  -> smallest vocab token ID on exact ties

Battery:
  30 cases
  prompt families:
    code
    reasoning
    prose
    structured
    dialogue

  context targets:
    64
    256
    1024
    4096
    8192
    16384

Total real MTP head decisions:
  3886

Q6 winner rank under Q5:
  rank 1: 3824
  rank 2:   61
  rank 3:    1
  rank 4+:   0

Recall:
  top1: 3824/3886 = 98.404529%
  top2: 3885/3886 = 99.974267%
  top4: 3886/3886 = 100.000000%

P42R5 Q6 decision equality:
  3886/3886 = 100.000000%

Observed failures:
  0

Max observed Q6 rank under Q5:
  3
