---
blueprint_kind: engineering
blueprint_status: draft
owner: TBD-ENGINEERING-001
last_reviewed: YYYY-MM-DD
---

# Engineering Rules

## Working principles

- State assumptions and surface conflicts before implementation.
- Prefer the smallest solution that meets confirmed requirements.
- Keep changes traceable to the requested requirement or defect.
- Define and run verification; do not claim success from inspection alone.

## Repository map

| Area | Path | Responsibility | Read before changing |
|---|---|---|---|

## Commands

| Purpose | Command | Scope/notes |
|---|---|---|
| Install | `[command]` | |
| Dev | `[command]` | |
| Unit tests | `[command]` | |
| Integration tests | `[command]` | |
| Typecheck/lint | `[command]` | |
| Build | `[command]` | |

## Code and dependency rules

- Language/framework conventions:
- Module boundaries:
- Error/logging conventions:
- Dependency approval/update policy:
- Generated code policy:

## Test and review gates

| Change type | Required tests/evidence | Reviewer/owner |
|---|---|---|

## Definition of done

- Related PRD/SPEC/ADR is current.
- Relevant automated and manual checks pass.
- Security, migration, observability and rollback impacts were considered.
- Only intentional changes remain in the diff.

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ENGINEERING-001 | Confirm canonical commands and quality gates | [role/name] | [date/milestone] | implementation-ready | pending |
