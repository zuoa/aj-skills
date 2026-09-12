# Artifact contract and traceability

## Authority map

| Artifact | Owns | Must not own |
|---|---|---|
| `PRD.md` | charter/source intent, feasibility assumptions, users, scope, outcomes, product requirements | internal technology and deployment topology |
| `SPEC.md` | global rules, layered index, delivery scope, dependencies, traceability, readiness | detailed domain behavior or implementation |
| domain specs under `specs/` | observable requirements, independently identified AC and validation evidence | framework, database, internal algorithms |
| `specs/interfaces/` | provider/consumer contract, business semantics, protocol source, compatibility | duplicated wire schemas or architecture decisions |
| `contracts/` | authoritative machine-readable interface definitions | duplicated Markdown field tables |
| `specs/tasks/` | implementation handoff, dependencies, change boundary, test plan and completion criteria | copied functional AC or unsolicited detailed algorithms |
| `DESIGN.md` | information architecture, interaction, visual direction, review evidence, implementation design source, UI states | backend internals |
| `ARCHITECTURE.md` | system boundaries, components, data flow, interfaces, quality budgets | product justification or visual styling |
| `SECURITY.md` | threats, data protection, identity controls, verification | generic legal conclusions |
| `DEPLOY.md` | environments, release, operations, recovery, cost | product behavior |
| `ENGINEERING.md` | contributor/agent workflow and quality gates | duplicated project requirements |
| ADR | durable high-impact decision and rationale | every reversible local choice |

When behavior changes, update PRD/SPEC first, then design/architecture/tasks/tests. Production findings may initiate that change but must not silently redefine behavior in DEPLOY.

## Stable identifiers

- Product requirement: `PRD-<DOMAIN>-NNN`
- Behavior specification: `SPEC-<DOMAIN>-NNN`
- Open decision: `TBD-<DOMAIN>-NNN`
- ADR: zero-padded sequence plus slug, e.g. `0001-session-strategy.md`

Never renumber an identifier after another artifact references it. Mark removed requirements as superseded and link the replacement.

## Spec decomposition and traceability

Read [spec-decomposition.md](spec-decomposition.md) when creating or auditing specs. New root SPEC files declare `spec_schema: 2`; absence retains legacy validation with migration guidance. Stable IDs additionally include `AC-<DOMAIN>-NNN`, `IFACE-<DOMAIN>-NNN` and `TASK-<DOMAIN>-NNN`.

Root SPEC indexes PRD → functional SPEC → AC → interface/task → test evidence, with links to DESIGN and ARCHITECTURE where applicable. AC is defined once under its owning SPEC; tasks reference IDs rather than copying assertions. Each interface and task references its source functional specs. Security or operational requirements enter this chain through an explicit PRD requirement linked to the authoritative control; do not manufacture a product rationale or leave the source untraceable.

Document the MVP capability map and current delivery scope separately. Future work may remain skeletal with a refinement trigger. Keep decision state (`confirmed / provisional / pending / not-applicable`), task readiness (`ready / blocked`), verification mode (`automated / manual / hybrid`) and execution result (`not-run / passed / failed / blocked`) distinct.

The machine-readable contract owns wire fields and schemas; interface Markdown owns semantic explanation and links. A source change requires impact review, not duplicate edits to several field lists. Tests and README link or derive from authoritative sources; generation and traceability reduce drift but do not prove its absence.

## Frontmatter

Canonical files use simple YAML frontmatter so tools can identify them without parsing headings in a particular language:

```yaml
---
blueprint_kind: prd
blueprint_status: draft
owner: team-or-role
last_reviewed: YYYY-MM-DD
---
```

Allowed `blueprint_kind` values are `prd`, `spec-index`, `domain-spec`, `design`, `architecture`, `security`, `deploy`, `engineering`, `adr`, `interface-spec`, and `task-spec`.

## Templates

Copy the closest file from `assets/templates/` and adapt it. Keep its frontmatter keys and traceability fields. Delete instructional placeholders that do not apply; record meaningful omissions as `not-applicable` rather than leaving empty headings.

DESIGN.md additionally uses `design_stage: direction / prototype / specification / not-applicable`. See `intake-and-status.md` for gates and `design-and-architecture.md` for evidence fields. `DESIGN_IMPLEMENTATION.md` is an optional template fragment merged into DESIGN.md after visual acceptance, not another required project document. Shared token definitions may remain in linked theme files or approved design-system references; DESIGN.md owns the choice and override policy.
