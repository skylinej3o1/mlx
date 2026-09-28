# Project 51 primary-lane research watch — 2026-09-28 18:00 ET

**Freshness boundary entering this pass:** **2026-09-28 21:39:35 UTC**.  
**User cutoff:** **2026-09-28 22:00:02 UTC**.

## Decision

**No new strict-window target or state change.**

The important quality change was already promoted in the immediately preceding pass:
- DASLab unpruned Flash-Next GSQ-RCO **IQ3_S** scored **82.0% SWE-bench Verified vs 82.8% BF16 (~99.0% retained)**.
- Project-51 therefore raised the **IQ3_S AA>=40 planning prior from ~75% to ~80%**.
- This is strong long-horizon agentic-coding evidence, but not direct 128K/262K long-context/state-continuity certification.

## Strict-window scan

From **21:39:35 -> 22:00:02 UTC**:
- **Strata:** no new release, exact-5070Ti ladder, or longer exact-card soak.
- **TensorFold:** no new commit after 0.3.6.2.
- **oMLX / mlx-serve / Ishizuki:** no new primary-lane commit.
- **vLLM:** only CI maintenance in-window; no P51-relevant runtime change.
- **SGLang / llama.cpp:** no new primary-lane commit.
- **DASLab/Hugging Face:** no newer official long-horizon result found beyond the already-promoted IQ3_S SWE-bench Verified 82.0/82.8 result.

## Canonical planning state

- Dual M1 Flash-Next: **40 TG @ genuinely filled ~128K / 400 cold PP / ~70% >=40 TG**.
- Single M1 dense27B: **25 TG / ~110 PP**.
- RTX5070Ti dense CUDA-v2 ladder unchanged.
- Strata Flash-Next ladder unchanged.
- IQ3_S custom-AA>=40 planning prior: **~80%**.

## New hard boundary

**2026-09-28 22:00:02 UTC**
