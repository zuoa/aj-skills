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

## Existing document conflict handling

Before editing, report:

| Topic | Existing statement | New evidence/request | Proposed resolution | Impacted files |
|---|---|---|---|---|

Preserve authored prose where it remains correct. Update the narrowest authoritative document, then repair references. If two sources disagree and authority is unclear, create a pending decision rather than picking silently.
