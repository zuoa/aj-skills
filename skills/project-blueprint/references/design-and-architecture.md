# Design and architecture guidance

## DESIGN.md

Design constraints should make later visual and interaction work decidable. Record:

- The concrete audience, context, and primary job for each important surface.
- Experience principles tied to user tasks, not generic adjectives.
- Information architecture, navigation, key journeys, and screen inventory.
- Reference products/assets and what to borrow or avoid from each.
- A visual thesis and at most one signature device that expresses something true about the product.
- A concrete overall palette: canvas/surface/text/border/action/focus/disabled/status tokens, exact values per supported theme, semantic use, interaction states, and required contrast pairs.
- A concrete typography system: font stacks and language fallbacks, source/license/loading, an exact size/line-height/weight/letter-spacing scale, responsive changes, and tabular-number or monospace rules where relevant.
- Component-level typography and geometry for every component used by the screen inventory. At minimum resolve Button, Input/Select, Navigation/Tabs, Table/List, Card, Dialog/Drawer, and Toast/Alert as applicable; include font token and resolved font/size, height/padding/gap, radius/border/elevation, states, source, and override policy.
- Spacing/grid, density, radius, elevation, motion, imagery, icon, and Emoji rules.
- Responsive breakpoints based on content behavior; safe areas and input modes for mobile.
- State matrix: loading, empty, error, partial, success, disabled, offline, permission denied, expired, and destructive confirmation.
- Accessibility target, normally WCAG 2.2 AA for web unless another requirement governs.
- Content voice, localization, text expansion, dates/numbers, RTL if applicable.

### Durable interaction principles

Use established usability heuristics as questions, not as slogans:

- Keep system status visible and distinguish pending, completed, failed, stale, and offline states.
- Use the user's language and domain objects instead of internal architecture terms.
- Preserve user control with cancel, back, undo, or confirmation in proportion to the consequence.
- Follow platform and product conventions unless a measured user benefit justifies divergence.
- Prevent high-cost errors before relying on error messages; when errors occur, state the result and recovery action.
- Prefer recognition over recall. Keep relevant context, choices, constraints, and history visible at the point of action.
- Support efficient repeat work without making first use depend on hidden shortcuts.
- Remove information and decoration that compete with the current task.

These principles do not choose a visual style. Connect each principle to a screen, behavior, or acceptance method.

### Subject-grounded visual direction

Do not manufacture a visual identity from “modern/minimal/premium.” Ask for concrete preferences such as editorial vs utilitarian, dense vs spacious, expressive vs restrained, and reference examples with reasons.

Before choosing colors, type, layout, or motion, state:

1. Who is using the surface and under what conditions.
2. The single job the surface must make easiest.
3. Which product or domain artifacts can supply visual language.
4. What to borrow and avoid from each reference, with a reason.

Use typography and layout to express hierarchy before adding decoration. Let one justified signature device carry the distinctive character; keep surrounding elements quiet and consistent. Minimal directions require precise spacing and type, while expressive directions require a coherent system rather than more effects.

### Minimum implementable visual system

`DESIGN.md` is an implementation contract, not a mood board. A developer should be able to style a representative screen without inventing colors, font sizes, or component hierarchy.

- Give color tokens concrete values such as HEX, RGB, HSL, or OKLCH. Define both foreground and background for status colors, and specify hover/pressed/selected/focus behavior. Record unsupported themes as `not-applicable`; do not silently omit them.
- Name the full font stack for each script the product supports. Record generic fallbacks, available weights, font delivery and license assumptions, and how the UI behaves while a web font loads.
- Express type sizes and line heights with implementation units; include a pixel reference when using `rem`. Define page title, section title, body, small body, label, action, helper/error, and data text when those roles appear.
- Map components to type tokens, then repeat the resolved family/size in the component table so reviewers can verify the result without following an undocumented token chain. Include long text, localization, zoom, truncation/wrapping, and numeric alignment where relevant.
- Record a base spacing unit and exact component measurements or tokens. A library name alone is insufficient because defaults, theme overrides, and versions can differ.

When brand inputs are missing, separate brand identity from implementation basics. Keep the brand identity pending, but choose an accessible provisional palette and system-font/type-scale baseline, state why it is safe enough for prototyping, and add an owner plus a measurable revisit trigger. Do not leave every visual token pending: that merely transfers the design decision to the implementer.

Before marking `implementation-ready`, verify representative desktop and mobile screens against the tables: computed fonts/sizes match, text at 200% zoom remains usable, supported themes meet the stated contrast targets, keyboard focus is visible on every surface, and status is understandable without color.

Treat gradients, glass effects, oversized rounded cards, repeated pill containers, decorative dashboards, arbitrary `01/02/03` labels, ambient animation, sparkles, robot mascots, and generic AI imagery as review signals. They are not forbidden, but each needs a product-specific reason. Remove any choice that would survive unchanged if the product name and industry were swapped.

### Content, icons, and motion

- Write from the user's side of the screen. Use active, specific action labels and keep terminology stable through the flow.
- Errors say what happened, whether work was saved or completed, and what the user can do next. Empty states direct a real next action rather than supply mood or encouragement.
- Default to a coherent platform-appropriate icon set. Critical or unfamiliar actions need visible text; icon-only controls need accessible names.
- Do not use Emoji in team-authored UI or system copy by default. Follow `output-quality.md` for allowed exceptions and their documentation.
- Use motion to explain a state or spatial relationship. Prefer one orchestrated moment over scattered effects; support reduced motion and avoid motion that blocks input or obscures status.

### Design self-critique

Before finalizing `DESIGN.md`, test the direction against the actual brief:

- Could the same palette, typography, cards, and hero be reused unchanged for an unrelated product? If yes, revise the generic choices.
- Does every structural marker encode order, state, grouping, ownership, or another true relationship? Remove decorative structure.
- Is the hierarchy still clear without color, imagery, and motion? Fix content order and typography first.
- Is boldness concentrated in one useful place? Remove competing accents.
- Are responsive, keyboard, focus, touch, long-text, loading, empty, error, offline, permission, and destructive states decidable and testable?

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
