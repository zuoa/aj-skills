# Constraint-driven technology selection

## Order of reasoning

1. State hard constraints: platform, region, compliance, deadline, team, budget, latency, availability, data and integration.
2. Separate constraints from preferences.
3. Show the three mandatory reference stacks and assess each against those constraints.
4. Establish the simplest viable baseline.
5. Add up to two analysis-derived candidates when the mandatory set misses a material requirement.
6. Recommend one candidate from the complete set, name its cost, and record a revisit trigger.
7. Present the comparison and recommended architecture/database/deployment package in the conversation. Apply the selection checkpoints in `intake-and-status.md`: obtain a choice or explicit delegation before treating the package as confirmed. A written recommendation or confirmed product constraints alone are insufficient.

## Mandatory reference stacks

Every full-stack technology selection must show these three candidates in this order. They are stable comparison anchors, not automatic winners.

| Candidate ID | Intended profile | Core stack | Typical strengths | Costs and review questions |
|---|---|---|---|---|
| `STACK-ENTERPRISE-JAVA-REACT` | Enterprise project | Java Spring Boot + React | Mature JVM ecosystem, explicit service boundaries, broad enterprise integration and governance support | Confirm Java/React capability, delivery overhead, runtime footprint, integration needs and whether organizational standards actually require it |
| `STACK-TOOL-FASTAPI-VUE` | Tool-oriented project | Python FastAPI + Vue SPA | Fast API delivery, Python library access and a separately evolvable interactive client | Confirm SPA complexity is justified, define API/client versioning, and account for two build/deploy surfaces |
| `STACK-RAPID-FLASK-JINJA` | Simple, rapid project | Python Flask + Jinja SSR | Small operational surface, direct server-rendered flows and low client-build overhead | Confirm the interaction model fits SSR, establish when frontend behavior or API consumers would force a split, and avoid growing ad hoc client code |

For each project:

- Keep all three rows even when one violates a hard constraint. Mark its fit as `not recommended` and name the conflicting constraint instead of silently removing it.
- Do not infer that “enterprise” automatically means Spring Boot, that every internal tool needs a SPA, or that Flask is acceptable merely because the first release is small. Team capability, interaction model, integrations, assurance needs and operating environment decide fit.
- Treat native or cross-platform mobile clients separately. The mandatory rows still compare the server and web/admin surface; add the actual mobile client candidate when mobile is in scope.
- Add no more than two analysis-derived alternatives when they materially improve constraint fit. Examples may include an existing organizational stack, a full-stack TypeScript framework, Django, Go, or a mobile-specific client, but only when the project facts justify them.
- Recommend one candidate across the mandatory and added alternatives. If evidence is insufficient, state the leading provisional option, the missing evidence and the decision deadline.

Use this comparison table before recording the decision:

| Candidate | Mandatory or derived | Constraint fit | Material advantages | Gaps/risks | Disposition |
|---|---|---|---|---|---|

Use this decision table:

| Decision | Hard constraints | Candidates | Recommendation | Tradeoff | State | Revisit trigger |
|---|---|---|---|---|---|---|

For confirmed selections, record the decision source, actual date and scope alongside this table. If the agent chose under explicit delegation, say so. Unanswered selections need a pending decision and must not make dependent implementation tasks ready, even when independent backend work is otherwise allowed by the visual-stage rules.

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
