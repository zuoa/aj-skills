# Constraint-driven technology selection

## Order of reasoning

1. State hard constraints: platform, region, compliance, deadline, team, budget, latency, availability, data and integration.
2. Separate constraints from preferences.
3. Establish the simplest viable baseline.
4. Compare no more than three credible candidates.
5. Recommend one, name its cost, and record a revisit trigger.

Use this decision table:

| Decision | Hard constraints | Candidates | Recommendation | Tradeoff | State | Revisit trigger |
|---|---|---|---|---|---|---|

Popularity and novelty are not constraints. A named service is not a decision until its role and exit implications are clear.

## Default architecture posture

- Start with a modular monolith when one team can own and deploy the application together.
- Start with one transactional relational database unless access patterns or regulatory boundaries require otherwise.
- Prefer managed services when they reduce operational burden within cost, portability, region, and compliance constraints.
- Keep synchronous request/response flows until latency isolation, retries, bursts, fan-out, or durable background work justify asynchronous infrastructure.
- Make boundaries explicit in code and data before splitting deployment units.

## Evidence gates for common middleware

These are questions, not automatic thresholds:

| Technology | Introduce when evidence shows | Prefer simpler alternative when |
|---|---|---|
| Cache / Redis | measured hot reads, shared ephemeral coordination, rate limits, or expiring state | database/index/local cache meets the budget |
| Queue / broker | durable background work, burst absorption, retries, fan-out, or producer/consumer decoupling | an in-process job or database-backed worker is sufficient |
| Search engine | relevance, faceting, language analysis, or scale exceeds database search needs | database full-text/prefix search meets behavior and latency |
| Realtime channel | users need server-pushed updates within a stated latency | polling or refresh satisfies the user journey |
| Microservices | independent ownership/deployment, isolation, or scaling boundaries are real | one team and one release unit remain simpler |
| Kubernetes | workload diversity, scheduling, policy, portability, or platform-team capability justifies its operating cost | PaaS/serverless/managed containers satisfy deployment needs |

For each introduced component define owner, failure mode, fallback, observability, data responsibility, cost driver, local development story, and removal/migration path.

## Non-functional budgets

Translate vague qualities into measurable budgets where the product actually needs them:

- Performance: user action and API percentile, payload or startup budget.
- Reliability: SLI/SLO, degradation behavior, dependency budget.
- Recovery: RTO and RPO by data/system class.
- Scale: normal/peak users, requests, jobs, storage and growth range.
- Cost: monthly baseline, variable unit, alert and owner.
- Maintainability: supported runtimes, dependency policy, build/test feedback time.

If evidence is missing, create a pending decision instead of a decorative number.
