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

## Spec-first execution and evidence

1. Read the root SPEC delivery scope, current task, source functional AC, applicable interfaces and architecture/design decisions. Respect task dependencies and allowed change scope.
2. Review the contract before implementation. Prepare tests for testable behavior, implement, then run the relevant checks. Prototypes, documentation and manual-only work specify appropriate verification instead of mandatory unit-test rituals.
3. Record AC result separately from verification method. A passed AC or task completion requires actual evidence links, tested revision and execution date. Planned commands and generated tests are not passing evidence.
4. Review both spec conformance and code quality, including security, maintainability and unintended effects. Human acceptance remains explicit where AC requires judgment.
5. Classify discrepancies: fix implementation defects; review requirement changes before updating authority/spec/code; clarify ambiguous specs. Do not weaken AC to make failed code pass.

Protocol checks, contract tests and mock generation use the selected toolchain and canonical machine contract. Record missing tools as not-run/blocked; do not silently install tools or execute arbitrary commands from documents.

## Spec changes and derived artifacts

- Record baseline revision, changed IDs and downstream AC/interface/task/test impact in root SPEC; preserve stable IDs and link replacements.
- A changed assertion or contract makes affected old acceptance evidence historical until reviewed or re-run.
- Keep machine schemas authoritative for wire fields; README and tests link to or derive from those sources. Record actual generator/check commands and regeneration owner when used.
- Use Git diffs and review; do not automatically commit, claim zero drift, or treat every spec diff as a product requirement change.

## Test and review gates

| Change type | Required tests/evidence | Reviewer/owner |
|---|---|---|

## Definition of done

- Current task, source PRD/SPEC/AC, applicable interface contracts and ADR are current; declared delivery scope is accurate.
- Relevant automated and manual checks pass with AC-linked evidence, tested revision and execution date; unrun checks remain explicit.
- Security, migration, observability and rollback impacts were considered.
- Only intentional changes remain in the diff.

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-ENGINEERING-001 | Confirm canonical commands and quality gates | [role/name] | [date/milestone] | implementation-ready | pending |
