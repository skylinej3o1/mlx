P44B1 — CERTIFIED ROBUST CHAMPION

Base:
  P43C G64 top4 reducer
  certified predecessor:
  project43c-g64-certified-28.820

Change:
  Search-head quantization only:

    P43C:
      Q5/G32
      weight: (248320, 800)
      scales: (248320, 160)
      biases: (248320, 160)

    P44B1:
      Q5/G64
      weight: (248320, 800)
      scales: (248320, 80)
      biases: (248320, 80)

Unchanged:
  P43C G64 hierarchical deterministic top4 reducer
  exact Q6/G32 x4 jury
  full-vocab tie semantics
  MTP model
  target verifier
  caches
  draft block size

Canonical behavior:
  generated tokens: 512
  rounds: 138
  text: e39b478ae4a8
  trajectory: f7801569fbdd
  jury calls: 414

Broad robustness:
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

  real MTP head decisions: 3886

  Q6-winner rank under Q5/G64:
    rank1: 3817
    rank2: 66
    rank3: 3

  max rank: 3
  top4 recall: 3886/3886
  exact Q6 jury: 3886/3886
  failures: 0

Direct 10-pair P43C Q5/G32 vs P44B1 Q5/G64:

  P43C G32 mean:
    28.824832 tok/s

  P44B1 G64 mean:
    28.953139 tok/s

  mean paired speedup:
    +0.4452%

  median paired speedup:
    +0.5223%

  wins:
    9/10

  all runs:
    rounds=138
    text=e39b478ae4a8
    trajectory=f7801569fbdd
    jury_calls=414

Promotion:
  PASS

Lineage-normalized champion estimate:
  ~28.95 tok/s
