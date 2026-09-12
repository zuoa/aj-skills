# Intake, decision status, and readiness

## Interview rhythm

Use the repository and supplied documents before asking questions. Ask in small groups, ordered by dependency:

1. Product intent and scope.
2. Clients, markets, data, and risk triggers.
3. Observable behavior and acceptance.
4. Experience and visual constraints.
5. Architecture and technical selection.
6. Security, delivery, and operations.

Ask only questions that change a decision or gate. Give 2–3 meaningful options when the user may not know the design space. Put the recommended option first and explain its consequence in one sentence.

## Minimum intake

### Product

- Product name or working title
- Target users and the job they need to complete
- Core journey and MVP boundary
- Explicit non-goals
- Success measures and acceptance owner
- Deadline, budget range, and team capability

### Clients and markets

- Web, responsive web, iOS, Android, mini-program, or cross-platform
- Public internet, enterprise/internal, tenant model, and expected geography
- China mainland, global, or both
- Offline behavior, push notifications, deep links, store distribution

### Data and integrations

- Data classes: public, internal, confidential, personal, sensitive personal, regulated
- System of record and retention/deletion expectations
- Identity, payments, files, messaging, maps, analytics, search, realtime, AI
- Third-party availability, lock-in, contract, quota, and exit constraints

### Quality and operations

- Traffic and data volume ranges; peak shape matters more than a vanity total
- User-visible latency and availability target
- RTO/RPO and acceptable degradation
- Cost ceiling and cost owner
- On-call/operations capacity and release frequency

Unknown numeric targets become a named pending decision. Never invent “99.99%” or a throughput target.

## Decision states

| State | Meaning | Required metadata |
|---|---|---|
| confirmed | User or authoritative source approved it | source and review date |
| provisional | Working default is acceptable for now | rationale and revisit trigger |
| pending | A decision is still required | `TBD-*` ID, owner, decision-by, blocked gate |
| not-applicable | The topic was examined and does not apply | short reason |

Use the localized labels in prose if needed, but preserve the English machine value in tables or frontmatter.

## Readiness ledger

Maintain one table in the root `SPEC.md`:

| Gate | Status | Blocking decisions | Evidence |
|---|---|---|---|
| design-ready | ready / blocked | TBD IDs or none | PRD sections |
| implementation-ready | ready / blocked | TBD IDs or none | SPEC/design/architecture sections |
| production-ready | ready / blocked | TBD IDs or none | security/deploy evidence |

Do not collapse the three gates. A project can be ready for design but not implementation, or ready for implementation but not production.

## Design stage and readiness

`DESIGN.md` carries `design_stage: direction / prototype / specification / not-applicable`, independently of decision states. Direction work may omit full visual values; prototype work adds a concrete handoff and honest review status. Only specification work requires accepted visual evidence and traceable implementation definitions. `not-applicable` requires an explanation that the project has no user-facing UI.

`design-ready` permits design and prototype exploration. For UI products, `implementation-ready: ready` means the applicable visual review is confirmed and its implementation source is recorded at specification stage, in addition to the existing product/architecture requirements. Direction/prototype work must not claim this gate is ready. This does not block independent backend work or isolated frontend exploration; state the allowed work in the handoff while the overall gate remains blocked. An approved design system may supply reusable evidence when its scope fits; record project-specific differences. Missing screenshots/tools mean unverified work, not automatic approval.

The machine stage values remain English. The root SPEC readiness table continues to use `ready / blocked`. Legacy DESIGN files without a stage retain the previous structural checks, with an informational migration note; adding an unknown or empty stage is an error, not a bypass.

## Existing document conflict handling

Before editing, report:

| Topic | Existing statement | New evidence/request | Proposed resolution | Impacted files |
|---|---|---|---|---|

Preserve authored prose where it remains correct. Update the narrowest authoritative document, then repair references. If two sources disagree and authority is unclear, create a pending decision rather than picking silently.

## Spec v2 delivery and task readiness

Root SPEC declares `spec_schema: 2`, a named `delivery_scope`, and comma-separated `current_specs`/`current_tasks` IDs. This is the scope of the existing readiness ledger, not a claim that the entire MVP is specified or finished. An empty current set is permitted in a blocked planning draft. Record later capabilities and refinement triggers separately; do not block the current delivery merely because unrelated later tasks remain skeletal.

Task `Readiness` concerns starting work, while `Completion` concerns executed results. A ready task has a complete current contract, confirmed source behavior and required interfaces, and relevant design/architecture decisions available. Dependencies must be satisfied before execution, even when several ready tasks are planned in the same delivery. Unfinished dependencies outside the selected scope prevent ready status; a completed prerequisite needs evidence. AC `not-run` is expected before implementation and is not itself a readiness blocker.

Keep root design/implementation/production gates and the visual-stage checks. Backend tasks can be ready while unrelated visual work is exploratory; the root gate must still reflect any unresolved visual work within the delivery. Structural spec validation does not run protocol validators or prove business correctness. Existing no-version specs retain legacy checks with a migration note; unknown versions are errors.
