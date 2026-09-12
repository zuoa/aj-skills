# Design and architecture guidance

## DESIGN.md: progressive design contract

Separate functional invariants, confirmed brand requirements, and visual suggestions open to exploration. Preserve known constraints, but do not manufacture pixel-level decisions to fill a template. Document restraint is an editing principle, not a requirement for neutral, sparse UI.

Use `design_stage` independently from decision states:

| Stage | Required output | Leave open |
|---|---|---|
| `direction` | Audience, primary jobs, journeys, shell relationships, visual direction, key customization, exploration boundaries | Exact typography, geometry, full palette, component styling |
| `prototype` | Direction plus viewable component/page preview and human review record; explicit handoff if delivery is deferred | Values and treatments still being tested |
| `specification` | Confirmed visual review plus an implementable shared token source and applicable component deltas | Only documented nonblocking refinements |
| `not-applicable` | Applicability section explaining why the project has no user-facing UI | Visual-only sections omitted; externally observable behavior stays in SPEC |

Start with `assets/templates/DESIGN.md`. Once the design is accepted, merge applicable sections from `assets/templates/DESIGN_IMPLEMENTATION.md` into DESIGN.md; do not copy it as another mandatory root artifact. Existing design systems may supply the implementation source and review evidence. Preserve the provenance and scope of their approval; do not invent new research or confirmation dates.

### Direction and customization

Use a reference-led direction the user can recognize, such as Apple-site-like product presentation or an enterprise dark workbench. Explain the characteristics to borrow: composition, type hierarchy, surface depth, content density, imagery, or motion. Adapt them to the actual task; a reference name and accent color alone are insufficient.

When the user has chosen a direction, refine it instead of reopening selection. Otherwise offer two or three plausible directions and one recommendation. The theme catalog is optional vocabulary, not a closed taxonomy. No weighted scoring is required for visual taste. Keep theme family, appearance, and density distinct; density can differ by region, and a dense work surface can coexist with a more expressive brand/search area.

Offer these directions in the conversation and follow the selection checkpoints in `intake-and-status.md`; listing a preferred and rejected style only in DESIGN.md is insufficient. Record the actual choice or delegation source and date. Without a reply, preserve the alternatives and pending selection rather than declaring “direction settled” or attributing rejected options to the user. A no-questions draft may recommend a provisional direction and prepare a conditional prototype handoff. Direction approval does not itself constitute visual acceptance of a prototype.

Record only consequential customization: brand/accent direction, display/body relationship, hierarchy and spacing rhythm, and a focal treatment where useful. Use signature devices when they express the product; neither a forced novelty quota nor a universal ban on decorative techniques improves design. Exact values are optional exploratory seeds until reviewed. Do not impose blanket rules such as one colored element per page, tiny headings, no shadows, or no brand imagery without an actual requirement.

Use `layout-catalog.md` when shell selection is unresolved. Keep layout family, navigation model, work-surface model, and platform chrome separate. Authentication/SSO/tenant controls need a place and behavior but do not determine the layout family. In direction work describe spatial relationships and compact transformation, not every pixel measurement.

### Visual preview and human review

After the direction is selected or selection is explicitly delegated, produce a lightweight design preview by default. This is an allowed blueprint artifact. Default to `design/preview.html` with inline CSS and minimal JavaScript, viewable by opening the file without a build step. Keep required assets local or embedded so the default preview does not depend on a CDN. Reuse an existing project's preview route when that better represents the selected components; provide its URL and exact startup instructions without scaffolding a new application. For native products, use an inspectable platform-appropriate prototype, or label an HTML approximation and leave native behavior unverified.

The preview contains two complementary views, normally in one file:

- Project-relevant components: semantic colors, type hierarchy, buttons, inputs, selection controls, cards, tags and applicable tables/dialogs/feedback. Show useful default, focus, disabled, loading and error states; omit unused components. Use the chosen direction instead of an unchanged library gallery.
- At least one representative business page: navigation, content hierarchy, information density and component composition around a primary task. Use real or clearly labeled representative content. Start with desktop and narrow-screen views where applicable; add materially different surfaces only as needed.

Provide simple local interactions where they affect judgment, such as tabs, filters, dialog open/close or form feedback. Use fixture data, with no real authentication, API writes or business services. A standalone visual approximation does not establish production component behavior or change the selected UI foundation; record differences for implementation. This exception does not authorize production business code, test implementations, running mock services or a complete scaffold.

In an H2 `Visual preview` / `视觉预览` section, record the page/task, components and states, target viewports, viewing instructions and expected reviewer. Use `Artifact` / `预览产物` for the Markdown link to the file or route. When no preview is delivered, use `Deferred reason` / `暂缓原因` to state the actual constraint and concrete handoff (owner, required artifact and next step). The earlier `Prototype handoff` / `样稿交接` heading is also accepted. A user request for documentation only takes precedence. Missing companion skills alone do not justify deferral; use the available HTML/file tools. If the direction is still pending, preserve the conditional brief without silently selecting it. API-only products skip visual work; approved evidence that fits the current scope may be reused without a redundant preview.

Open and inspect the rendered preview with available browser tools before requesting confirmation. Check desktop/narrow layouts and the interactions actually provided. Deliver the viewing link, current revision, scope and unresolved questions, then request human review from the user or designated design owner. Complete the preview before this request; permission to make a preview is already implied by blueprint work after direction selection. If rendering tools are unavailable, still deliver the viewable artifact where possible and mark browser checks unverified. If the user requested no questions, deliver the preview with review pending and a named follow-up instead of inventing acceptance.

Retain the project accessibility target (normally WCAG 2.2 AA for Web), platform requirements and relevant loading/empty/error/permission/offline/destructive states throughout all stages.

Review the rendered page for hierarchy, composition, spacing rhythm, reference fidelity, brand recognition, and task usability. Check responsive behavior, keyboard/focus and relevant states separately. A screenshot supports visual review, not a claim of keyboard or interaction testing. Keep evidence attached to the tested revision. Record what changed and whether another review is needed.

Use these localized or English fields in an H2 `Visual review` / `视觉评审` section (one current record; older history can be linked):

- Review status / 评审状态: `pending`, `provisional`, or `confirmed`.
- Evidence / 证据: Markdown links to the reviewed screenshot, prototype, or approved design-system reference; pending reviews may omit unavailable evidence.
- Reviewed revision / 评审版本: identifiable preview revision, commit, content hash, dated snapshot, or approved design-system version/baseline.
- Confirmed scope / 确认范围: components, representative page(s), states, viewports and appearances actually accepted, including exclusions or project-specific deltas.
- Reviewer / 评审人: the actual reviewer or authorized source.
- Reviewed on / 评审日期: actual review date (`YYYY-MM-DD`).
- Findings and adjustments / 结论与调整: accepted treatment, open issues, and scope of evidence.

`confirmed` requires evidence, reviewed revision, confirmed scope, reviewer, date, and a review conclusion. A bare status label is insufficient. Existing approved design-system evidence may be reused with its actual version or approval baseline, applicability and project-specific deltas stated; do not require redundant redesign or invent a version. If evidence cannot be inspected, keep the review pending/provisional and deliver the artifact or handoff. No screenshot, filled parameter table, source-code inspection, or agent self-check alone constitutes human/authoritative approval. Explicit delegation of visual acceptance must be recorded as delegated review, not a user review; delegation of direction selection alone does not cover it.

Keep the approved revision retrievable through a versioned artifact, snapshot or commit. When the preview changes in a way that affects accepted visuals or behavior, preserve the old approval as history and return the affected scope to pending/provisional for another review. A file with the same name does not inherit approval for new content. Only then derive or update the implementation specification from the newly accepted baseline.

The validator checks the record's structure and local link existence, not aesthetic quality, remote availability, approval authenticity, or image contents. Human/agent review remains required.

### Specification from accepted work

After visual acceptance, derive the system used by implementation:

- A `Token source` / `Token 来源` section links to the authoritative theme/config/design-system source, or an inline token section via an anchor. Include appearance, ownership, and permitted override boundaries.
- Color and typography sections contain the relevant semantic palette, contrast/state rules, font stacks, fallbacks/loading, and responsive type scale, or link directly to the maintained source. Do not duplicate external or shared definitions merely to satisfy tables.
- Component specifications map used components to shared type/geometry tokens or named foundation variants and record only product-specific deltas and important states. Do not repeat resolved font families and numbers on every row. A token reference must resolve to a documented source.
- Define supported appearances, spacing/grid, radius/elevation and motion as used by the accepted design. Verify actual text, long content, narrow layouts, zoom, status cues and focus against the source.

Color, typography, UI foundation and component sections remain structural checks at specification stage. The source and values can live in maintained code or an approved system; a phrase such as “use brand colors” without a concrete definition or source is not a contract. No exhaustive tables are required during direction or prototype work.

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

### Frontend UI foundation

For a React or Vue client with more than trivial interaction, select a coherent UI component foundation when preparing an interactive prototype and confirm it before implementation. A component foundation may be a styled suite, an open-code distribution system, a headless primitive layer plus project styling, or an existing organizational design system. It is not enough to write “custom CSS” or list several libraries without choosing one.

For Flutter, React Native, Jetpack Compose, or SwiftUI, make the same decision at
the platform level: identify the framework theme source, semantic role mapping,
component-style/override boundary, system appearance and accessibility inputs,
and which geometry remains platform-native. Shared brand tokens do not require
identical component anatomy across Web, Android, and Apple platforms.

Use the product and delivery constraints to choose the mode:

| Need | Candidate family to evaluate | Typical tradeoff |
|---|---|---|
| Product-facing UI with a distinctive visual identity | React: shadcn/ui with its current official primitive foundation; Vue: shadcn-vue with Reka UI | More visual control and source ownership; the team owns theme quality, component updates, and composition discipline |
| Data-dense or enterprise workflow needing broad coverage quickly | React: MUI or Ant Design; Vue: PrimeVue or Element Plus | More complete components and conventions; stronger risk of a generic vendor look unless tokens and component variants are deliberately themed |
| Existing organization-wide design system | The existing supported system | Consistency and lower adoption cost; confirm it covers the current framework, accessibility target, and required components |
| Tiny or constrained surface | Themed semantic HTML plus a small CSS system | Lowest dependency cost; unsuitable when the team would need to rebuild complex focus, keyboard, overlay, or selection behavior |

These names are starting candidates, not timeless defaults. Check current official documentation during the blueprint run for framework compatibility, maintenance status, SSR/hydration constraints, accessibility claims, licensing, theming API, import strategy, and required peer dependencies. Record the access date when the decision depends on changeable facts.

By specification stage, the decision in `DESIGN.md` must name:

- the selected foundation and whether it is styled, open-code, headless, or organizational;
- at least one credible alternative and why it lost under the actual constraints;
- the theme/token entry point, one SVG icon set, ownership and update policy;
- the available primitive/semantic/component token layers or equivalents,
  appearance and density mechanism, scoped-theme behavior, SSR/no-flash path,
  and permitted override boundary;
- coverage for every complex primitive used by the screen inventory, including Select/Combobox, Menu, Tabs, Dialog/Drawer, Popover/Tooltip, Toast/Alert, form validation, and Table/Pagination when applicable;
- bundle/import, SSR/hydration, localization, keyboard/focus, and test implications that materially affect the project.

Do not confuse semantic native HTML with unstyled browser UI. Keep native semantics where appropriate, but do not ship browser-default controls as the visual system. Complex primitives must come from an accessibility-capable foundation or have an explicit, testable implementation and maintenance plan. Do not mix component suites casually: if an exception is necessary, document visual normalization, focus behavior, z-index/portal ownership, and who maintains the integration.

The component foundation is an implementation substrate, not the visual thesis. Theme its tokens and variants to the product-specific direction, then verify a representative desktop and mobile screen. A library's default demo appearance is not sufficient evidence that the result meets the selected direction; review the representative composition.

### Content, icons, and motion

- Write from the user's side of the screen. Use active, specific action labels and keep terminology stable through the flow.
- Errors say what happened, whether work was saved or completed, and what the user can do next. Empty states direct a real next action rather than supply mood or encouragement.
- Default to a coherent platform-appropriate icon set. Critical or unfamiliar actions need visible text; icon-only controls need accessible names.
- Do not use Emoji in team-authored UI or system copy by default. Follow `output-quality.md` for allowed exceptions and their documentation.
- Use motion to explain a state or spatial relationship. Prefer one orchestrated moment over scattered effects; support reduced motion and avoid motion that blocks input or obscures status.

### Design self-critique

- Does the rendered hierarchy and spacing express the selected direction, or only the component library defaults?
- Are brand expression and content density appropriate in each region, rather than uniformly minimized?
- Can people identify the main task and complete it without competing visual emphasis?
- Are meaningful visual improvements being rejected only because exploratory numbers were written too early? Revisit those numbers before constraining the composition.
- Is each acceptance claim supported by the right evidence, and are untested states clearly identified?

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

- Functional SPEC/AC says what an actor can observe; architecture says how responsibilities collaborate to make it true. Interface specs link the canonical wire contract; task specs reference the necessary architecture decisions instead of copying them.
- A technical limitation that changes observable behavior must return to PRD/SPEC for approval.
- Link architecture sections from the traceability matrix instead of copying scenarios.
- Architecture tests validate boundaries and quality attributes; behavior tests validate SPEC scenarios.
