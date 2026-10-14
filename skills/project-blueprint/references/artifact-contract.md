# Artifact contract and traceability

## Authority map

| Artifact | Owns | Must not own |
|---|---|---|
| `PRD.md` | charter/source intent, feasibility assumptions, users, scope, outcomes, product requirements | internal technology and deployment topology |
| `SPEC.md` | navigation, current changes, delivery scope, traceability, blueprint readiness | competing behavior definitions or an OpenSpec schema |
| `openspec/specs/<capability>/spec.md` | implemented behavior baseline: requirements and scenarios | future behavior, framework, database, internal algorithms |
| `openspec/changes/<change>/proposal.md` | motivation, scope, new/modified capabilities and impact | detailed implementation or copied PRD |
| change `specs/<capability>/spec.md` | proposed behavior deltas and acceptance scenarios | implementation plan or claims of implementation |
| change `design.md` | change-specific technical approach, tradeoffs and migration | project visual authority or copied long-term architecture |
| change `tasks.md` | numbered implementation checklist, dependencies and verification | copied requirements or unsupported completion claims |
| `docs/interfaces/` (when needed) | provider/consumer semantics, protocol source, compatibility | duplicated wire schemas or architecture decisions |
| `contracts/` | authoritative machine-readable interface definitions | duplicated Markdown field tables |
| `openspec/config.yaml` | OpenSpec schema selection and context/rules routing to project sources | duplicated decisions or a second project specification |
| `DESIGN.md` | information architecture, interaction, visual direction, review evidence, implementation design source, UI states | backend internals |
| `design/preview.html` or linked preview route/prototype | inspectable component and representative-page design evidence, with local demo interactions | production business logic or approval claims; DESIGN.md owns review status and scope |
| `ARCHITECTURE.md` | system boundaries, components, data flow, interfaces, quality budgets | product justification or visual styling |
| `SECURITY.md` | threats, data protection, identity controls, verification | generic legal conclusions |
| `DEPLOY.md` | environments, release, operations, recovery, cost | product behavior |
| `ENGINEERING.md` | contributor/agent workflow and quality gates | duplicated project requirements |
| ADR | durable high-impact decision and rationale | every reversible local choice |

When behavior changes, adjust product intent if needed and open/update an OpenSpec change before implementation. Update its deltas, technical design and tasks with impact on project documents and tests. Merge deltas into the implemented baseline after implementation and verification, using the project's OpenSpec sync/archive workflow. Production findings must not silently redefine behavior in DEPLOY. Root `DESIGN.md` and change `design.md` have separate responsibilities even on case-insensitive filesystems because they are in separate directories.

## Stable identifiers

- Product requirement: `PRD-<DOMAIN>-NNN`
- Behavior specification: `SPEC-<DOMAIN>-NNN`
- Open decision: `TBD-<DOMAIN>-NNN`
- ADR: zero-padded sequence plus slug, e.g. `0001-session-strategy.md`

Never renumber an identifier after another artifact references it. New OpenSpec requirement/scenario titles may carry `SPEC-*` / `AC-*`; retain existing titles exactly, since delta matching uses the requirement name. Record removal/replacement history in the change rather than retaining removed requirements in the live baseline.

## Spec decomposition and traceability

Read [spec-decomposition.md](spec-decomposition.md) when creating or auditing specs. New root SPEC files declare `spec_framework: openspec`, `delivery_scope`, and comma-separated `current_changes` names (`none` for a blocked planning draft). These are blueprint index fields, not OpenSpec schema fields. Existing unversioned/spec v2 files retain legacy validation; migrate explicitly. Native OpenSpec files do not require `blueprint_kind` or the old scalar field envelope.

Root SPEC indexes PRD → capability/change → requirement/scenario → task → evidence, with links to DESIGN, ARCHITECTURE and contracts where applicable. Define each AC under its owning Requirement; tasks refer to its ID or exact title and file link. Every active behavior change identifies source PRD requirements in its proposal or requirement. Security/operational behavior uses a product requirement linked to the authoritative control; do not manufacture rationale for a pure implementation change.

Document the MVP capability map and current delivery scope separately. Future work may remain in the roadmap with a refinement trigger. Keep decision state (`confirmed / provisional / pending / not-applicable`), blueprint readiness (`ready / blocked`), verification mode (`automated / manual / hybrid`) and execution result (`not-run / passed / failed / blocked`) distinct. OpenSpec artifact completion only means files exist; checked tasks record implemented work, not permission or acceptance.

The machine-readable contract owns wire fields and schemas; interface Markdown owns semantic explanation and links. A source change requires impact review, not duplicate edits to several field lists. Tests and README link or derive from authoritative sources; generation and traceability reduce drift but do not prove its absence.

## Frontmatter

Root blueprint documents, ADRs and optional interface notes use simple YAML frontmatter. Native OpenSpec proposal/spec/design/tasks use their native headings and checklist without mandatory blueprint frontmatter:

```yaml
---
blueprint_kind: prd
blueprint_status: draft
owner: team-or-role
last_reviewed: YYYY-MM-DD
---
```

Current `blueprint_kind` values are `prd`, `spec-index`, `design`, `architecture`, `security`, `deploy`, `engineering`, `adr`, and `interface-spec`. `domain-spec` and `task-spec` remain supported only for legacy validation. Native OpenSpec files need no blueprint frontmatter.

## Templates

Copy the closest file from `assets/templates/` and adapt it. Keep its frontmatter keys and traceability fields. Delete instructional placeholders that do not apply; record meaningful omissions as `not-applicable` rather than leaving empty headings.

DESIGN.md additionally uses `design_stage: direction / prototype / specification / not-applicable`. See `intake-and-status.md` for gates and `design-and-architecture.md` for evidence fields. `DESIGN_IMPLEMENTATION.md` is an optional template fragment merged into DESIGN.md after visual acceptance, not another required project document. Shared token definitions may remain in linked theme files or approved design-system references; DESIGN.md owns the choice and override policy.

External DESIGN.md analyses remain references: adapt their useful characteristics into the project's existing DESIGN.md rather than replacing its metadata, decisions or review record. Keep reference provenance separate from project acceptance. The design's Agent implementation brief routes to the accepted baseline, token source and component rules; it does not duplicate ENGINEERING/AGENTS or business SPEC. Preview and implementation consume the designated visual definitions, and material differences return to design review.
