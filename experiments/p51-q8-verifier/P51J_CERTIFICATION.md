# P51J — Warmed verifier-routing certification

## Ruler

- Model: Jundot/Qwen3.8-27B-oQ8e-fp16-mtp
- Hardware: M1 Max 32-core GPU / 64 GB
- Prompt: 29,297 tokens
- Completion: 512 tokens
- Fixed speculative depth: D2 / M=3
- QMM mode: all
- K parts: 2
- Warm-up: one 16-token request before measurement

## Default routing

| Run | TG tok/s | Backbone ms/cycle | Hash |
|---|---:|---:|---|
| D1 | 15.419 | 150.653 | f42ac9dd2bdf9d5a |
| D2 | 15.743 | 148.767 | f42ac9dd2bdf9d5a |
| D3 | 15.456 | 150.532 | f42ac9dd2bdf9d5a |

Mean:

- TG: 15.539 tok/s
- Backbone: 149.984 ms/cycle

All runs used 217 cycles.

## ALL-MEDIUM routing

Additional exact routed shapes:

- K=17408 -> N=5120
- K=5120 -> N=10240
- K=5120 -> N=6144
- K=5120 -> N=12288

| Run | TG tok/s | Backbone ms/cycle | Hash |
|---|---:|---:|---|
| A1 | 16.916 | 137.273 | f46220cfe4923fc1 |
| A2 | 16.903 | 137.383 | f46220cfe4923fc1 |
| A3 | 16.874 | 137.571 | f46220cfe4923fc1 |

Mean:

- TG: 16.898 tok/s
- Backbone: 137.409 ms/cycle

All runs used 217 cycles.

## Certified delta

Relative to warmed default routing:

- TG gain: +8.74%
- Backbone/cycle reduction: -8.38%

ALL-MEDIUM won all three paired comparisons.

## P51I subtractive attribution

Using ALL-MEDIUM bookends as the local control:

- Removing 5120->10240:
  +4.93 ms/cycle backbone penalty; ~-3.45% TG
- Removing 5120->6144:
  +2.35 ms/cycle backbone penalty; ~-1.64% TG
- Removing 5120->12288:
  +1.57 ms/cycle backbone penalty; ~-1.00% TG

Conclusion:

All three medium routes contribute. 5120->10240 is the
largest individual contributor.

## Numerical behavior

Default routing produced deterministic hash:

f42ac9dd2bdf9d5a

ALL-MEDIUM produced deterministic hash:

f46220cfe4923fc1

Default accepted 293/392 drafts; ALL-MEDIUM accepted 294/392.
A broader deterministic/quality corpus remains required before
production freeze.
