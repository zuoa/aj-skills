---
blueprint_kind: interface-spec
blueprint_status: draft
owner: TBD-IFACE-001
last_reviewed: YYYY-MM-DD
---

# Boundary Contract

## IFACE-CORE-001 — [boundary capability]

- Source: SPEC-CORE-001
- State: pending
- Provider: [module/service]
- Consumer: [module/client]
- Protocol: [confirmed protocol or pending decision]
- Contract: [Markdown link to authoritative OpenAPI/protobuf/JSON Schema; in-process-only boundaries may explain not-applicable]
- Operations: [operation/schema symbols mapped to SPEC/AC; link field definitions rather than duplicate them]
- Auth: [authentication and authorization semantics or reasoned non-applicability]
- Errors: [error meaning and caller recovery]
- Compatibility: [versioning, compatibility and migration policy]
- Contract checks: [protocol validator/compiler, contract-test/mock entrypoints and commands, or missing-tool status]
- Result: not-run

Add relevant pagination, retry, idempotency, timeouts, ordering and duplicate-event rules. Machine definitions own wire fields; ARCHITECTURE owns module/data design. Actual protocol validation results use Evidence, Tested revision and Executed on; no tool/run means no passing claim.

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-IFACE-001 | Confirm boundary and protocol | [role/name] | [date/milestone] | implementation-ready | pending |
