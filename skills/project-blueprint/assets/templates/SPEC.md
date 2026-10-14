---
blueprint_kind: spec-index
spec_framework: openspec
delivery_scope: TBD-SPEC-001
current_changes: none
blueprint_status: draft
owner: TBD-PRODUCT-001
last_reviewed: YYYY-MM-DD
---

# Blueprint Index and Delivery Scope

## Authority and navigation

PRD owns product intent; OpenSpec owns behavior and change artifacts; root DESIGN owns UI/UX; ARCHITECTURE owns durable internal design. This index links their authority and records blueprint readiness. OpenSpec change design.md is the technical approach for that change, distinct from root DESIGN.md.

- OpenSpec configuration: [openspec/config.yaml](openspec/config.yaml)
- Implemented behavior: `openspec/specs/<capability>/spec.md` (may be empty for a greenfield project)
- Proposed work: `openspec/changes/<change-name>/`
- Machine contracts: `contracts/`; optional semantic notes: `docs/interfaces/`

## Glossary and shared rules

| Term / rule | Meaning | Authoritative source |
|---|---|---|

## MVP capability map and current delivery

- Current outcome and exclusions:
- Dependencies and execution order:
- Later capabilities, risks and refinement triggers:

| Capability | Outcome | Current/later | Baseline or change link | Dependencies / refinement trigger |
|---|---|---|---|---|

## Change index

Keep current_changes frontmatter synchronized with the selected delivery. List active changes with links to their proposal/specs/design/tasks; distinguish draft, ready-for-implementation and executed completion without treating artifact existence as acceptance.

| Change | Scope | Artifacts | Decision source / readiness |
|---|---|---|---|

## Traceability

Use IDs for new blueprints; preserve exact titles when referencing an existing OpenSpec baseline. Link definitions rather than copying assertions. PRD requirements planned for later delivery remain explicitly traced to the roadmap.

| PRD ID | Capability / change | Requirement / scenario | Task reference | Design / architecture / contract | Verification evidence |
|---|---|---|---|---|---|

## Change impact

| Baseline revision | Changed requirement/scenario | Reason: defect/requirement/ambiguity | Affected contracts/tasks/tests | Compatibility / migration | Review state |
|---|---|---|---|---|---|

## Readiness ledger

| Gate | Status | Blocking decisions | Evidence |
|---|---|---|---|
| design-ready | blocked | TBD-PRODUCT-001 | PRD.md |
| implementation-ready | blocked | TBD-SPEC-001 | Current change and design/architecture decisions |
| production-ready | blocked | TBD-DEPLOY-001 | SECURITY.md; DEPLOY.md |

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SPEC-001 | Confirm the current change scope and observable behavior | [role/name] | [date/milestone] | implementation-ready | pending |
