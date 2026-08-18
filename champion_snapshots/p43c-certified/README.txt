P43C — CERTIFIED ROBUST CHAMPION

Base:
  P42R5 robust top4/Q6 jury

Change:
  Top4 reducer stage1 geometry:
    P42R5: 256 groups x 256 threads
            TOTAL_THREADS=65536
            stage2 NCAND=1024

    P43C:   64 groups x 256 threads
            TOTAL_THREADS=16384
            stage2 NCAND=256

Algorithm unchanged:
  Q5/G32 full-vocab search projection
  deterministic top4 selection
  exact Q6/G32 x4 jury
  full-vocab tie semantics

Canonical behavior:
  512 generated tokens
  rounds=138
  text=e39b478ae4a8
  traj=f7801569fbdd
  jury calls=414

10-pair direct P42R5 vs P43C:
  P42R5 mean: 28.784395 tok/s
  P43C mean:  28.802659 tok/s

  mean paired:   +0.0635%
  median paired: +0.0749%
  wins:           7/10

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

  total real MTP head decisions: 3886

  Q5 winner rank:
    rank1: 3824
    rank2: 61
    rank3: 1

  top4 recall:
    3886/3886

  P43C exact Q6 decision:
    3886/3886

  failures:
    0

Promotion:
  P43C = robust development champion.

Certified predecessor:
  project42r5-top4-certified-28.801

Lineage-normalized observed estimate:
  ~28.820 tok/s
