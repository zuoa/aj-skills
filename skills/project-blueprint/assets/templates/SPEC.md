---
blueprint_kind: spec-index
spec_schema: 2
delivery_scope: TBD-SPEC-001
current_specs: none
current_tasks: none
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: YYYY-MM-DD
---

# Specification Index and Delivery Scope

## Scope and authority

This index owns shared rules, layered navigation, current delivery scope and traceability. PRD owns charter/product intent; ARCHITECTURE owns internal design; domain specs own behavior and AC; interfaces own boundary semantics; tasks own implementation handoff. Keep machine schemas in their authoritative contract files. Do not duplicate layer contents.

## Glossary

| Term | Meaning | Source |
|---|---|---|

## Global behavior rules

| Rule ID | Observable rule | Source | State |
|---|---|---|---|

## MVP capability map and delivery scope

- Scope named by frontmatter; current outcome and exclusions:
- Dependency order and scope assumptions:
- Later capabilities and refinement triggers:

| Capability / SPEC ID | Outcome | Current/later | Dependencies | Refinement trigger |
|---|---|---|---|---|

## Layered specification index

List every functional SPEC, AC, IFACE and TASK ID with its definition link; group related entries without copying requirements. Keep current_specs/current_tasks frontmatter in sync with this delivery's chosen scope.

| Layer / ID | Definition / source | Owner | Decision state |
|---|---|---|---|

## Traceability

| PRD ID | SPEC ID | AC IDs | Interface IDs | Task IDs | Design/architecture source | Verification evidence |
|---|---|---|---|---|---|---|

## Change impact

| Baseline revision | Changed IDs | Reason: defect/requirement/ambiguity | Affected AC/interfaces/tasks/tests | Compatibility/migration impact | Review state |
|---|---|---|---|---|---|

## Readiness ledger

| Gate | Status | Blocking decisions | Evidence |
|---|---|---|---|
| design-ready | blocked | TBD-PRODUCT-001 | PRD.md |
| implementation-ready | blocked | TBD-SPEC-001 | specs/core.md |
| production-ready | blocked | TBD-DEPLOY-001 | SECURITY.md; DEPLOY.md |

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SPEC-001 | Confirm the current delivery scope and observable behavior | [role/name] | [date/milestone] | implementation-ready | pending |
