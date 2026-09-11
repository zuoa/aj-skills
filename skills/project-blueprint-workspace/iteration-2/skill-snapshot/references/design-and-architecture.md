# Design and architecture guidance

## DESIGN.md

Design constraints should make later visual and interaction work decidable. Record:

- Experience principles tied to user tasks, not generic adjectives.
- Information architecture, navigation, key journeys, and screen inventory.
- Reference products/assets and what to borrow or avoid from each.
- Typography roles, color semantics, spacing/grid, radius, elevation, motion, imagery, and icon rules.
- Component source: existing design system, chosen library, custom components, and override policy.
- Responsive breakpoints based on content behavior; safe areas and input modes for mobile.
- State matrix: loading, empty, error, partial, success, disabled, offline, permission denied, expired, and destructive confirmation.
- Accessibility target, normally WCAG 2.2 AA for web unless another requirement governs.
- Content voice, localization, text expansion, dates/numbers, RTL if applicable.

Do not manufacture a visual identity from “modern/minimal/premium.” Ask for concrete preferences such as editorial vs utilitarian, dense vs spacious, expressive vs restrained, and reference examples with reasons.

### Mobile branch

Confirm native vs cross-platform from constraints rather than habit:

- Required OS versions, device classes, native APIs, background execution, offline data and synchronization.
- Push, deep links, universal/app links, biometrics, camera/location/notification permissions.
- Store accounts, signing, review lead time, privacy disclosures, staged rollout and forced/minimum version policy.
- Platform conventions that should remain native versus brand elements that stay shared.

## ARCHITECTURE.md

Use the smallest C4-style views that clarify boundaries:

1. System context: users, system, external systems, trust boundaries.
2. Containers/deployable units: web/mobile clients, API, workers, stores and external services.
3. Component or dynamic views only for complex/high-risk flows.

Diagrams supplement prose. Every box and arrow needs a responsibility or protocol; avoid decorative “layered architecture” diagrams.

Record:

- Module boundaries and owners.
- Source of truth and data ownership.
- API/event contracts, versioning and compatibility.
- Transaction, idempotency, consistency and concurrency expectations.
- Authentication/session boundary and authorization model.
- File, search, cache, background work, realtime and third-party integration decisions.
- Failure/degradation behavior and dependency timeouts/retries.
- Quality attribute budgets and evidence.
- Evolution triggers: the condition that would justify splitting or replacing a component.

## Relationship to SPEC

- SPEC says what an actor can observe; architecture says how responsibilities collaborate to make it true.
- A technical limitation that changes observable behavior must return to PRD/SPEC for approval.
- Link architecture sections from the traceability matrix instead of copying scenarios.
- Architecture tests validate boundaries and quality attributes; behavior tests validate SPEC scenarios.
