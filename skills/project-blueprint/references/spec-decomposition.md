# OpenSpec decomposition, contracts, and evidence

## Directory and authority

Use the official OpenSpec `spec-driven` schema for new blueprints. Existing configured schemas and integration files take precedence; inspect them before writing. `SPEC.md` remains a blueprint index and readiness ledger, not another specification engine. PRD owns product intent, ARCHITECTURE/ADR own durable architecture, and root DESIGN owns UI/UX.

```text
PRD.md, SPEC.md, DESIGN.md, ARCHITECTURE.md, SECURITY.md, DEPLOY.md, ENGINEERING.md
openspec/
  config.yaml
  specs/<capability>/spec.md                    # Implemented behavior baseline
  changes/<change-name>/
    proposal.md                                # Why / what / impact
    design.md                                  # Change-specific technical approach
    tasks.md                                   # Numbered implementation checklist
    specs/<capability>/spec.md                  # Proposed behavior deltas
  changes/archive/                             # Completed change history
contracts/                                     # Canonical wire definitions, when needed
docs/interfaces/                              # Optional semantic contract notes
```

A greenfield blueprint normally has an empty baseline and an initial change containing ADDED deltas. Do not write future behavior into the implemented baseline or archive a plan. Existing implemented behavior may be documented as a baseline after checking code, tests and scope; distinguish observed facts from assumptions. Reuse existing capability paths, including nested paths where the project uses them. New segments and change names use kebab-case. Task/interface notes must not live under OpenSpec `specs/`, which contains behavior specs only.

Use [SPEC.md](../assets/templates/SPEC.md) for the index, [OPENSPEC_CONFIG.yaml](../assets/templates/OPENSPEC_CONFIG.yaml) for project routing, [PROPOSAL.md](../assets/templates/PROPOSAL.md), [DELTA_SPEC.md](../assets/templates/DELTA_SPEC.md), [CHANGE_DESIGN.md](../assets/templates/CHANGE_DESIGN.md) and [TASK_SPEC.md](../assets/templates/TASK_SPEC.md) for changes. [DOMAIN_SPEC.md](../assets/templates/DOMAIN_SPEC.md) is only for an implemented baseline. [INTERFACE_SPEC.md](../assets/templates/INTERFACE_SPEC.md) is an optional note outside OpenSpec specs.

## Setup and artifact flow

Reuse `openspec/config.yaml` and installed OpenSpec integrations. For a new project, `schema: spec-driven` plus `context` and artifact `rules` is sufficient; do not fork a schema merely to add PRD/design links or blueprint readiness. Generate the files directly when the CLI is unavailable. Installing the CLI, updating agent integrations and generating business scaffolding are not prerequisites for drafting a blueprint.

When using a CLI, inspect its version/help and work in the target project root. Setup and agent command delivery vary by installed version/tool; use `openspec init --help` and preserve existing agent instructions. Prefer CLI instructions over assumptions about slash commands. Typical artifact commands are:

```bash
openspec list --specs
openspec list
openspec new change <change-name> --schema spec-driven
openspec status --change <change-name> --json
openspec instructions proposal --change <change-name> --json
openspec instructions specs --change <change-name> --json
openspec instructions design --change <change-name> --json
openspec instructions tasks --change <change-name> --json
```

Read relevant baseline specs in full before drafting deltas. Proposal precedes specs and technical design; tasks consume both. Dependencies guide preparation, without requiring a fixed interview order. Existing custom schemas may allow a simpler change without design; follow the resolved schema rather than manufacturing content.

## Capability, requirement and scenario format

Group by cohesive, independently reviewable system behavior; split on ownership, interface or delivery boundaries, not on file count or fixed work duration. Prefer vertical outcomes across client/API/storage. Detail the current slice; keep future capability goals, sources, dependencies, risks and refinement triggers in the roadmap.

The native syntax is required even when prose is Chinese:

```markdown
### Requirement: SPEC-BOOKING-001 Reserve an available slot
The system SHALL create a reservation only if the slot is still available.

#### Scenario: AC-BOOKING-001 Successful reservation
- GIVEN a signed-in member and an available slot
- WHEN the member submits a reservation
- THEN exactly one reservation is visible in that member's list
```

Use exactly H3 `Requirement:` and H4 `Scenario:`. Each ADDED/MODIFIED requirement needs at least one scenario and normative SHALL/MUST behavior. Use optional GIVEN plus explicit WHEN/THEN. New baseline specs use `## Purpose` and `## Requirements`; change deltas use `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`, and/or `## RENAMED Requirements`. A new capability delta includes a meaningful Purpose; an existing capability keeps its baseline Purpose.

The current default strict validator expects Purpose to contain at least 50 characters and flags new requirement descriptions longer than 500 characters. Put concrete examples and edge cases in scenarios. Preserve existing MODIFIED blocks intact; do not trim or split an existing requirement merely to satisfy a length warning. Recheck limits against the installed CLI when they matter.

Stable PRD/SPEC/AC IDs are useful blueprint traceability, not extra OpenSpec grammar. Preserve existing names and IDs. Link source PRD in the proposal or `- Source:` under a requirement; link task/scenario definitions from root SPEC. Keep requirement descriptions short and behavior-focused; frameworks, databases, classes and algorithms belong in technical design. Cover relevant failures, boundaries, permissions, duplicate requests, concurrency, partial results and recovery. Unknown thresholds are named TBDs, not invented numbers.

MODIFIED replaces the entire matched requirement: copy its exact title and **all scenarios**, then edit the complete block. ADDED is for new behavior rather than partial edits to existing requirements. REMOVED includes Reason and Migration. RENAMED uses `- FROM: ` plus a backtick-quoted old title and `- TO: ` plus a backtick-quoted new title; when behavior also changes, include MODIFIED under the new title. Never rename existing titles just to retrofit IDs.

## Acceptance and interface evidence

Each scenario states a decidable outcome. For current delivery, add `Verification: automated / manual / hybrid`, `Procedure`, and `Evidence required`; Fixture/Assertion may be explicit fields when GIVEN/THEN alone do not explain reproduction. Manual/hybrid acceptance names `Acceptance owner`. Use `Result: not-run / passed / failed / blocked` separately from the verification method. Passing claims require linked Evidence, actual Tested revision and valid Executed on date/time. Do not insert run-specific reports into stable baseline specs unless the project deliberately owns evidence there; a change's `verification.md` or existing report can retain execution records linked by scenario.

No tests or running mock services are generated by this skill. Command text, generated tests, source inspection or a checked task do not prove acceptance. Visual and business judgments keep their named human acceptance owner. Existing reports become historical when affected assertions/contracts change, until review or re-run.

For a known protocol, use or generate the canonical machine contract under `contracts/`. Markdown interface notes explain provider/consumer, authentication, error semantics, compatibility and applicable retry/idempotency/ordering rules without duplicating field schemas. Change design/tasks link that contract and the source behavior. Unknown protocols block dependent work; in-process boundaries may explain why no wire schema applies. Protocol validation uses the project's selected official toolchain, never arbitrary commands executed by the structural checker.

## Tasks and readiness

`tasks.md` uses numbered checkbox tasks (`- [ ] 1.1 ...`). Each current outcome references its requirement/scenarios, necessary dependencies, allowed change scope, design/architecture/contracts and verification procedure. Optional `TASK-*` IDs can remain in task text; no per-task spec files are required. UI tasks link root DESIGN's accepted revision, scope and implementation brief. Keep local coding choices open.

Root SPEC uses `spec_framework: openspec`, a named `delivery_scope`, and comma-separated `current_changes` (`none` for an explicitly blocked draft). This selects delivery scope without redefining OpenSpec's lifecycle. All current scenarios need task coverage; an enabling task can share a scenario while describing its contribution. Dependencies run in order. A file-complete OpenSpec change may still be blocked by product, architecture, interface or visual decisions. Not-run acceptance is normal before implementation.

The downstream loop is: review change and constraints → prepare applicable tests → implement tasks → run checks and record evidence → review completion → sync/archive with OpenSpec. Fix code for implementation defects; update deltas and review impact for requirement changes; clarify ambiguity. Do not weaken scenarios to make failing code pass. Archive/sync is an implementation handoff action, never a shortcut to finish the blueprint.

## Validation and migration

Run the blueprint supplement, then official native validation separately when available:

```bash
python3 <skill-path>/scripts/validate_blueprint.py <project-root>
# In the target project root:
openspec validate --all --strict --no-interactive
```

The supplement checks project links, scope, readiness, traceability and evidence; it neither runs document commands nor substitutes for OpenSpec's parser/delta validation. Report each result independently. A missing CLI means native checks are not-run, not passed. Structural validation does not prove business correctness or UI acceptance.

For existing unversioned or `spec_schema: 2` blueprints, preserve checks until explicitly migrating. Map old functional SPEC/AC headings into native Requirement/Scenario headings without changing meaning; separate observed implemented behavior from planned changes; move task content into change `tasks.md` and interface notes into `docs/interfaces/`; keep machine contracts. Update root index metadata, agent routes and relative links together. Preserve referenced history, acceptance reports and IDs; do not delete old files until references have been accounted for. Do not maintain two active behavior authorities after migration.
