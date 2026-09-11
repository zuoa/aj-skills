# Skill Benchmark: project-blueprint

**Model**: <model-name>
**Date**: 2026-09-10T07:25:16Z
**Evals**: 1, 2, 3, 4 (1 run per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
|--------|------------|---------------|-------|
| Pass Rate | 100% ± 0% | 70% ± 35% | +0.30 |
| Time | 0.0s ± 0.0s | 0.0s ± 0.0s | +0.0s |
| Output characters | 65869 ± 20778 | 29582 ± 20336 | +36287 |

## Analyst observations

- With-skill outputs passed all 20 expectations; baseline outputs passed 14 of 20.
- The largest gain appears in the vague-project eval: stable PRD/SPEC IDs, traceability, registered TBDs, and explicit readiness gates.
- The mobile eval passed in both configurations, so future assertions should test cross-document consistency and unsupported numeric defaults in addition to topic coverage.
- Strong baselines already handle architecture well; the skill adds behavior-level scenarios, document authority boundaries, and explicit production blockers.
- With-skill output is substantially longer. A future compact mode would reduce review burden without weakening the contract.
- Timing and model-token telemetry were unavailable; the size metric above is output characters, used only as a review-cost proxy.
