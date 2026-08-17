P42C CERTIFIED CHAMPION
=======================

Architecture:
  Q5/G32 full-vocab draft-head search
  -> hierarchical Metal top-2 reduction
       stage 1: 256 x 256-thread groups
       stage 2: reduce 512 partial candidates
  -> certified Q6/G32 exact rerank of 2 rows
  -> greedy token

Canonical behavior:
  rounds:     138
  text hash:  e39b478ae4a8
  traj hash:  f7801569fbdd
  jury calls: 414/run

10-pair certification:
  P41E mean:          28.681635 tok/s
  P42C mean:          28.828303 tok/s

  mean paired:        +0.5114%
  median paired:      +0.5078%
  wins:               10/10
  behavioral cert:    PASS

Pair percentages:
  +0.578%
  +0.444%
  +0.577%
  +0.551%
  +0.628%
  +0.446%
  +0.504%
  +0.408%
  +0.467%
  +0.511%

Previous certified P41E mean:
  28.628993 tok/s

Applying P42C paired uplift to prior P41E certification:
  ~28.775 tok/s lineage-normalized
