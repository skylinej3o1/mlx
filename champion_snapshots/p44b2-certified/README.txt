P44B2 — CERTIFIED ROBUST CHAMPION

Predecessor:
  project44b1-q5g64-certified-28.95

Change:
  approximate full-vocabulary search head only

P44B1:
  Q5/G64
  W=(248320,800)
  S=(248320,80)
  B=(248320,80)

P44B2:
  Q4/G32
  W=(248320,640)
  S=(248320,160)
  B=(248320,160)

Unchanged:
  P43C hierarchical G64 deterministic top4 reducer
  exact Q6/G32 x4 gathered jury
  full-vocabulary tie semantics
  target verifier
  MTP model
  draft block size
  caches

Canonical:
  generated=512
  rounds=138
  text=e39b478ae4a8
  trajectory=f7801569fbdd
  jury_calls=414

Broad robustness:
  cases=30
  real head decisions=3886
  rank1=3800
  rank2=81
  rank3=5
  max_rank=3
  top4_recall=3886/3886
  exact_q6_jury=3886/3886
  failures=0

Direct 10-pair P44B1 Q5/G64 vs P44B2 Q4/G32:
  P44B1 mean=28.930412
  P44B2 mean=29.044437
  mean paired=+0.3942%
  median paired=+0.4231%
  wins=10/10

All timed runs:
  rounds=138
  text=e39b478ae4a8
  trajectory=f7801569fbdd
  jury_calls=414

Promotion:
  PASS

Current robust champion:
  29.044 tok/s direct paired-session mean
