---
blueprint_kind: architecture
blueprint_status: draft
owner: TBD-ARCH-001
last_reviewed: YYYY-MM-DD
---

# System Architecture

## Constraints and quality budgets

| Attribute | Target/range | Evidence | State | Revisit trigger |
|---|---|---|---|---|

## System context

[C4-style context diagram plus responsibilities and trust boundaries]

## Containers and deployable units

| Unit | Responsibility | Interfaces | Data owned | Owner | State |
|---|---|---|---|---|---|

## Module boundaries

| Module | Responsibility | Allowed dependencies | Related SPEC |
|---|---|---|---|

## Data and consistency

| Data/entity | Source of truth | Classification | Consistency/transaction | Retention |
|---|---|---|---|---|

## Interfaces and integrations

| Interface ID/source | Machine contract reference | Data-flow/module responsibility | Key architectural tradeoff | Related SPEC |
|---|---|---|---|---|

Boundary semantics and wire fields belong to the linked interface spec and machine contract; this section owns internal responsibility and data flow. Record implementation constraints needed by task specs without predesigning every local algorithm.

## Technology and middleware decisions

### Full-stack candidates

Keep the three mandatory reference stacks in every full-stack selection. Add up to two constraint-derived rows when useful; do not delete a mandatory row merely because it is not recommended.

| Candidate | Mandatory or derived | Constraint fit | Material advantages | Gaps/risks | Disposition |
|---|---|---|---|---|---|
| Java Spring Boot + React | mandatory — enterprise reference | | | | |
| Python FastAPI + Vue SPA | mandatory — tool reference | | | | |
| Python Flask + Jinja SSR | mandatory — simple/rapid reference | | | | |

### Decisions

| Decision | Hard constraints | Candidates | Recommendation | Tradeoff | State | Revisit trigger |
|---|---|---|---|---|---|---|

## Failure and evolution

- Expected degradation:
- Capacity boundaries:
- Split/replace triggers:

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ARCH-001 | Confirm architecture owner and baseline | [role/name] | [date/milestone] | implementation-ready | pending |
