# Artifact contract and traceability

## Authority map

| Artifact | Owns | Must not own |
|---|---|---|
| `PRD.md` | users, problem, scope, outcomes, product requirements | internal technology and deployment topology |
| `SPEC.md` | global behavior rules, glossary, domain index, traceability, readiness | detailed domain behavior or implementation |
| `specs/*.md` | externally observable requirements and scenarios | framework, database, internal modules |
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

## Domain spec contract

Every confirmed domain requirement includes:

1. Spec ID and title.
2. Source PRD ID(s).
3. Decision state.
4. Normative requirement stated as observable behavior.
5. Preconditions and actors when relevant.
6. At least one normal scenario.
7. Failure, boundary, permission, concurrency, offline, or recovery scenarios when relevant.
8. Observable result and acceptance method.

Use Given/When/Then to remove ambiguity, not to inflate obvious statements. Never specify invisible implementation details in a scenario.

## Traceability

The root `SPEC.md` contains:

| PRD ID | SPEC ID | Design evidence | Architecture evidence | Test status |
|---|---|---|---|---|

- One PRD requirement may map to several specs.
- A spec without a PRD source needs an explicit source such as security/compliance/operational requirement.
- Design and architecture evidence may be section anchors rather than duplicated text.
- Test status uses `planned / automated / manual / passed / deferred` and must not claim `passed` without evidence.

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

Allowed `blueprint_kind` values are `prd`, `spec-index`, `domain-spec`, `design`, `architecture`, `security`, `deploy`, `engineering`, and `adr`.

## Templates

Copy the closest file from `assets/templates/` and adapt it. Keep its frontmatter keys and traceability fields. Delete instructional placeholders that do not apply; record meaningful omissions as `not-applicable` rather than leaving empty headings.

DESIGN.md additionally uses `design_stage: direction / prototype / specification / not-applicable`. See `intake-and-status.md` for gates and `design-and-architecture.md` for evidence fields. `DESIGN_IMPLEMENTATION.md` is an optional template fragment merged into DESIGN.md after visual acceptance, not another required project document. Shared token definitions may remain in linked theme files or approved design-system references; DESIGN.md owns the choice and override policy.
