P44B3 — CERTIFIED ROBUST CHAMPION

Predecessor:
  project44b2-q4g32-certified-29.04

Change:
  approximate search-head group size only

P44B2:
  Q4/G32
  W=(248320,640)
  S=(248320,160)
  B=(248320,160)

P44B3:
  Q4/G64
  W=(248320,640)
  S=(248320,80)
  B=(248320,80)

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
  rank1=3782
  rank2=94
  rank3=9
  rank4=1
  max_rank=4
  top4_recall=3886/3886
  exact_q6_jury=3886/3886
  failures=0

Direct 10-pair P44B2 Q4/G32 vs P44B3 Q4/G64:
  P44B2 mean=29.057401
  P44B3 mean=29.201393
  mean paired=+0.4956%
  median paired=+0.4830%
  wins=10/10

All timed runs:
  rounds=138
  text=e39b478ae4a8
  trajectory=f7801569fbdd
  jury_calls=414

Promotion:
  PASS

Current robust champion:
  29.201 tok/s direct paired-session mean
