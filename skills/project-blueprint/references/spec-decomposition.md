# Spec decomposition, contracts, and evidence

## Scope and authority

Use PRD as the charter/source of intent and ARCHITECTURE/ADR as the architectural spec. Do not create competing copies named charter or architecture spec. A functional spec owns observable behavior, an interface spec owns boundary semantics, and a task spec owns implementation handoff. See [artifact-contract.md](artifact-contract.md).

This skill creates specifications and machine-readable contracts, not business code, tests or running mocks. Inspect existing artifacts first. Generate a contract only for a known interface/protocol; verify the selected protocol's current official documentation when its syntax/version matters. Preserve existing schema conventions and toolchains. Do not install or run tools just because a document contains a command.

Use [DOMAIN_SPEC.md](../assets/templates/DOMAIN_SPEC.md) for behavior/AC, [INTERFACE_SPEC.md](../assets/templates/INTERFACE_SPEC.md) for boundaries and [TASK_SPEC.md](../assets/templates/TASK_SPEC.md) for work packages. The root [SPEC template](../assets/templates/SPEC.md) owns scope and indexes. Copy only the templates applicable to this delivery.

## Split by independently verifiable outcomes

1. Map MVP capabilities, business boundaries, shared invariants and dependencies. Identify current delivery scope separately from the whole MVP.
2. Group closely related behavior in `specs/<domain>.md`. Split a large domain into `specs/<domain>/<capability>.md` when ownership, independent review, interface boundaries or delivery timing justify it. Never split just to meet a line count.
3. Prefer a vertical task that can demonstrate a result across UI/API/storage. Separate shared infrastructure, a schema migration or an interface when it has a real independent contract and verification. Reference the related functional requirement even for enabling tasks.
4. Split a task containing unrelated outcomes, incompatible permissions, different blocking dependencies or independently deployable changes. Do not make one spec per function/file or force identical task durations.
5. Fully specify near-term tasks after relevant architectural and interface choices exist. Later tasks keep goal, source, dependencies, risk and refinement trigger. Do not prewrite speculative algorithms or exact file lists for an unexplored repository.

For example, “booking” can contain availability lookup, reservation creation and cancellation. A reservation task may span form, API and persistence while sharing one outcome and its failure AC. A prerequisite slot-uniqueness migration can be separate if it has its own invariant and verification. Avoid independent “write all frontend / write all backend” tasks that cannot demonstrate a complete result.

## Machine-readable envelope

Use the following simple scalar frontmatter fields in root SPEC (comma-separated IDs, not YAML arrays):

```yaml
spec_schema: 2
delivery_scope: first-booking-slice
current_specs: SPEC-BOOKING-001
current_tasks: TASK-BOOKING-001, TASK-BOOKING-002
```

`none` is allowed for an honest planning draft with blocked implementation readiness. All tasks not selected in `current_tasks` are later work. Every referenced dependency must be defined; current tasks must include unfinished dependencies in the delivery scope. Dependencies outside the current set may be reused only with `Completion: passed` and actual completion evidence. Current coverage is determined from AC belonging to `current_specs`, not from an arbitrary subset chosen by an implementing agent.

New domain/interface/task files use `blueprint_kind: domain-spec / interface-spec / task-spec`. Discover them recursively under `specs/` by kind. Interface files belong in `specs/interfaces/`, task files in `specs/tasks/`; a task file contains exactly one TASK definition. Ignore untyped README/index helpers. Root PRD/SPEC, existing blueprint kinds and command-line options remain unchanged.

Use H2 functional headings `SPEC-<DOMAIN>-NNN`, H3 AC headings `AC-<DOMAIN>-NNN` inside their parent SPEC, and H2 interface/task headings `IFACE-<DOMAIN>-NNN` / `TASK-<DOMAIN>-NNN`. IDs are globally unique within their prefix and never renumbered. Mark a retired definition with `Superseded by: <same-prefix replacement ID>` and retain its last decision state; do not add superseded to the four decision states or reuse the ID. Retired definitions remain indexed as history and must not be selected for current implementation.

The bullet-field labels below are stable English parser keys even when descriptions are Chinese. Use plain `- Field: value` lines. Record identifier lists comma-separated and absence as `none`. Additional narrative, diagrams and scenario subheadings are welcome. Do not put instructional placeholders into ready artifacts.

## Functional spec and AC

Every functional SPEC records `Source` (PRD IDs), `State`, `Actors`, `Trigger`, `Preconditions`, `Inputs`, `Rules`, and `Outcome`. Keep normative behavior observable; architecture owns mechanisms. Add invariants and state-transition tables when they clarify behavior. Future capabilities may be pending with a refinement plan; current capability omissions are reported.

Each AC belongs to its nearest parent SPEC and contains its own Given/When/Then scenario plus:

| Field | Meaning |
|---|---|
| Verification | `automated / manual / hybrid`; this is a method, not a result |
| Fixture | Data and environment needed to reproduce the scenario |
| Assertion | Observable result, including relevant state/data effects |
| Procedure | Test command or reproducible manual steps; prospective tests may use a planned command |
| Evidence required | Expected test report, response, screenshot or human acceptance record |
| Acceptance owner | Required for manual/hybrid judgment |
| Result | `not-run / passed / failed / blocked` |
| Evidence | Actual Markdown links; required only when claiming passed |
| Tested revision | Actual tested source/spec revision; required when passed |
| Executed on | Actual ISO date, optionally with ISO time; required when passed |

Cover normal behavior and applicable failure, boundary, permission, duplicate, concurrency, partial-result and recovery cases. Explain meaningful omissions; do not generate irrelevant cases. Unknown business thresholds remain explicit pending decisions. “Works correctly” is not an assertion. All AC must be decidable, but business acceptance and aesthetic judgment need not be automated.

Passed means an actual run or authorized manual review produced the required evidence for the tested revision. A screenshot does not prove keyboard behavior. Command text, generated tests, a green checklist or source inspection alone are not execution evidence. A functional spec can be ready before its AC run; `not-run` does not block starting implementation.

## Interface spec and protocol source

Each IFACE records `Source` (SPEC IDs), `State`, `Provider`, `Consumer`, `Protocol`, `Contract`, `Operations`, `Auth`, `Errors`, `Compatibility`, and `Contract checks`.

Use `Contract` Markdown links to authoritative OpenAPI, protobuf or JSON Schema under `contracts/`, or an existing authoritative project contract. An in-process interface with no wire schema may use `not-applicable: <reason>`; a missing/undecided schema is pending, not not-applicable. State why a given format is needed; do not emit all three formats for every interface.

Document error semantics, authentication/authorization and version evolution; add pagination, retry, timeout, idempotency, event ordering and deduplication only where relevant. Map operations/schema symbols back to functional SPEC/AC. Markdown explains these semantics and points at the machine contract rather than duplicating its field definitions. ARCHITECTURE keeps internal data ownership, module boundaries and design tradeoffs.

`Contract checks` names the project's protocol validator/compiler and the intended contract-test/mock generation entrypoints or their non-applicability. Record protocol validation using `Result`, `Evidence`, `Tested revision`, `Executed on`, with the same meanings as AC. The structural checker verifies references and JSON syntax when the linked source is local JSON; it does not implement OpenAPI/protobuf/schema semantic validation. YAML/protobuf semantic checks require the selected external tool; no tool available means not-run/blocked, never passed. External commands are not automatically executed by the structural checker.

## Task spec and readiness

Each task file defines one TASK. All tasks record `Source` (SPEC IDs), `Goal`, `Depends on` (TASK IDs or none), `Risk`, and `Refine when`. A fully specified task may use `Refine when: none — already detailed`.

Current tasks additionally record:

| Field | Meaning |
|---|---|
| State | `confirmed / provisional / pending / not-applicable` |
| AC | AC IDs this work implements or enables; AC must belong to Source specs |
| Interfaces | IFACE IDs or none, consistent with Source specs |
| Non-goals | Explicit exclusion from this task |
| Change scope | Relevant modules/files when known, with allowed/excluded boundaries |
| Constraints | Necessary architecture/design/security/deploy links and implementation invariants; leave local coding choices open |
| Test plan | Spec-first test approach, applicable unit/integration/contract/manual checks and commands |
| Done when | AC/evidence and other concrete completion conditions |
| Readiness | `ready / blocked` for starting this task, independent of whether code has been written |
| Completion | `not-run / passed / failed / blocked` for executed completion |
| Evidence, Tested revision, Executed on | Required when Completion is passed |

A task may start when its source behavior/AC and relevant interfaces are confirmed, its necessary design/architecture decisions are available and its external dependencies are satisfied. `ready` does not mean dependencies inside the current plan can be skipped; execute in dependency order. Mark unresolved blocking decisions as TBD and keep readiness blocked. Later skeletal work does not need a full test plan.

Coverage requires each current AC to appear in at least one current task. An enabling task may share an AC with a feature task; describe its contribution instead of claiming to independently satisfy the entire feature. Multiple tasks may share a functional outcome. Root SPEC lists all definitions and file links for navigation; it need not repeat every assertion.

## Execute, review, change

The downstream workflow is: review spec and current task → prepare applicable behavior/contract tests → implement → run checks → record AC results → review completion. Prototype, documentation and manual-only work name the appropriate verification instead of pretending every task needs a failing unit test first.

Code review checks both contract conformance and implementation quality: security, maintainability, unintended effects and actual test adequacy still matter. AI may execute available checks and report differences; a person remains responsible where acceptance calls for human judgment.

Classify a discrepancy before editing the contract: implementation defect → fix code; changed requirement → update authoritative spec and review impact; ambiguity → clarify the decision. Never weaken AC automatically to make failed code pass.

Root SPEC maintains a change-impact ledger: baseline revision, changed IDs, reason/type, affected AC/interfaces/tasks/tests, compatibility/migration impact, and review state. Use Git history/diffs; do not invent commits or automatically commit. Changed assertions or contracts invalidate affected prior acceptance claims until reviewed/re-run; retain old reports as historical evidence. Mark replaced IDs as superseded and link replacements.

README and tests may link to or derive from the same sources. Record generator/check commands when actually used and who owns regeneration. Traceability and generated artifacts reduce drift; neither guarantees drift is impossible.
