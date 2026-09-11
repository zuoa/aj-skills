# Skill Benchmark: project-blueprint

**Executor model**: unavailable (historical isolated runs)  
**Analyzer model**: GPT-5 Codex  
**Date**: 2026-09-11T01:41:30Z  
**Evals**: 1, 5, 6, 7 (1 run per configuration)

## Summary

| Metric | With skill | Iteration-1 snapshot | Delta |
|---|---:|---:|---:|
| Pass rate | 100% | 85% | +15 percentage points |
| Time | 625.4s ± 297.1s | 314.1s ± 314.9s | +311.3s |
| Output characters | 20,874 ± 8,623 | 18,006 ± 11,195 | +2,869 |

## Per-eval quality

| Eval | With skill | Snapshot | Difference |
|---|---:|---:|---:|
| 1 — vague coach SaaS regression | 5/5 | 5/5 | 0 |
| 5 — bookstore design | 5/5 | 4/5 | +1 |
| 6 — AI ops design | 5/5 | 4/5 | +1 |
| 7 — Emoji exception | 5/5 | 4/5 | +1 |

## Analyst observations

- Current skill passed all 20 expectations; the iteration-1 snapshot passed 17 of 20.
- The gains are narrow and intentional: task-grounded visual references, one justified signature device, and an auditable Emoji-exception approval state.
- Eval 1 passed in both configurations, so the design-focused revision preserved the original blueprint contract.
- The snapshot already handled many design basics well. Assertions about avoiding generic decoration, actionable state copy, and accessibility often pass in both configurations and are less discriminating.
- Eval 7's snapshot run stopped after PRD, SPEC, DESIGN, and domain specs. Its design assertions remain gradeable, but completeness and runtime comparisons for that case are unreliable.
- Timing is approximate or includes timeout/recovery work in several runs. It is not a meaningful performance result.
- Model token counts were unavailable. “Output characters” is the exact size of final text artifacts and serves only as a review-cost proxy.
- There is one run per configuration per eval. The variation shown above is across different evals, not repeated-run variance.
