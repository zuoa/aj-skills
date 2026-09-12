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

### Selection checkpoints

Product scope, technical architecture, and UI direction are separate decisions. Before concluding intake, check for a current user choice or explicit delegation for each applicable selection. Without one, present candidates in the conversation and ask the user to choose or delegate. A comparison buried in generated files does not complete this interaction. There is no fixed number of interview rounds after which selection can be skipped.

- Architecture: present the three reference stacks required by `selection-rubric.md`, any useful derived alternatives, and a recommended package covering architecture shape, database and deployment. Let the user accept the package or amend it; local implementation details do not need a questionnaire.
- UI: present two or three recognizable directions describing composition/navigation, appearance, color and typography character, with a recommendation. A product's audience or entertainment category does not establish its owner's visual preference. Direction selection and later prototype visual acceptance are distinct checkpoints.
- Reuse an explicit prior choice or approved design system when its source and scope apply. Memory and old generated documents are leads to verify, not evidence that the user approved a new baseline. An installed framework establishes a repository fact, not user approval of every associated design decision.
- Wait for the answer before finalizing the dependent decision or marking dependent tasks ready. Independent product/spec work can continue. A generic “continue” only authorizes the next action actually presented; it does not retroactively approve choices never offered.
- If the user requests no questions or a direct draft, comply with provisional recommendations and named pending decisions. If the user explicitly delegates selection, decide within that scope and record an agent decision under delegation. Do not invent a user review or require redundant permission.

Store the source and actual date alongside each consequential selection in its authoritative document: the user's choice, an applicable approved source, or the explicit delegation and agent rationale. Keep UI direction and architecture separately traceable even when answered in one message. Do not write “confirmed in interview” based only on product answers.

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

An official technical source can establish compatibility or availability; it cannot approve a project's preferences. A delegated decision may be confirmed within the user's authorization, with that provenance stated. An unanswered recommendation remains provisional with a pending selection; it does not unblock work that requires a confirmed architecture or design direction.

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

`DESIGN.md` carries `design_stage: direction / prototype / specification / not-applicable`, independently of decision states. Direction work may omit full visual values; prototype work normally delivers a viewable component/page preview and human review request, or an explicit reason and handoff when deferred. Review remains pending until actual acceptance, tied to the reviewed revision and scope. Only specification work requires accepted visual evidence and traceable implementation definitions. Material preview changes reopen affected visual acceptance; historical approval is not proof for a changed artifact. `not-applicable` requires an explanation that the project has no user-facing UI.

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
