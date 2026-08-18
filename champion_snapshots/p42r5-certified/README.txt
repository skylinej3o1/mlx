P42R5 — ROBUST TOP-4 Q5/Q6 JURY
================================

Architecture:
  Q5/G32 full-vocabulary search
  -> deterministic hierarchical Metal top-4
  -> gather four certified Q6/G32 rows
  -> exact Q6 scoring
  -> highest score, lowest token ID on exact ties

ROBUSTNESS BATTERY
------------------
Cases:
  30

Prompt families:
  code
  reasoning
  prose
  structured
  dialogue

Context:
  64 through 16384 tokens

Real MTP head decisions:
  3886

Q6 winner rank under Q5:
  rank 1: 3824
  rank 2:   61
  rank 3:    1
  rank 4+:   0

Top-4 recall:
  3886 / 3886
  100.000000%

P42R5 exact Q6 decisions:
  3886 / 3886
  100.000000%

Observed robustness failures:
  0


LIVE 10-PAIR CERTIFICATION
--------------------------
Canonical:
  rounds: 138
  text hash: e39b478ae4a8
  trajectory hash: f7801569fbdd
  jury calls: 414

Every certification run:
  canonical behavior PASS

P42C:
  28.834
  28.825
  28.824
  28.849
  28.854
  28.841
  28.838
  28.852
  28.839
  28.844

P42R5:
  28.790
  28.828
  28.792
  28.850
  28.799
  28.806
  28.792
  28.804
  28.784
  28.768

P42C mean:
  28.840021 tok/s

P42R5 mean:
  28.801384 tok/s

P42R5 paired delta vs P42C:
  mean:   -0.1340%
  median: -0.1556%
  wins:    2 / 10

PROMOTION:
  P42R5 = robust development champion.

P42C remains a useful raw-speed reference, but it is not
eligible for robust promotion because the broader decision
battery exposed failures.
