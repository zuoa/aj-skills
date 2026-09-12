# Frontend companion skills

Use companion skills as a routed capability stack. They complement the blueprint contract; they do not replace confirmed product decisions, source verification, or the readiness gates.

## Dependency model

These are project-level companion skills, not application runtime packages and not automatic dependencies of `project-blueprint`. Do not add an unsupported `depends_on` field or list them under `agents/openai.yaml` `dependencies.tools`, which is reserved for tool dependencies.

If a relevant companion is installed, use it at the matching stage. If it is unavailable, continue with this skill's own design guidance and report the missing review or implementation capability in the handoff. Never install external skills silently while producing a blueprint.

## Routing

| Companion skill | Apply when | Contribution | Do not use as |
| --- | --- | --- | --- |
| `ui-ux-pro-max` | A Web or interactive client needs a design-system direction, palette/type/layout candidates, interaction patterns, or stack-aware UX guidance | Structured candidate generation and searchable UI/UX knowledge before finalizing `DESIGN.md` | An automatic final answer or evidence that a candidate fits the product without checking the brief |
| `frontend-design` | The work needs a distinctive visual thesis, hierarchy, typography, composition, preview creation, or visual critique | Subject-grounded visual direction, component/page previews and anti-template critique | A substitute for accessibility checks, behavioral specs, or human visual acceptance |
| `web-design-guidelines` | Existing Web UI/code is being audited, or an implementation is ready for pre-delivery review | Web interaction, content, accessibility, responsive, and interface-quality review | A planning requirement for API-only, native-only, or not-yet-implemented work |
| `vercel-react-best-practices` | `package.json` or a confirmed decision establishes React or Next.js and implementation/performance rules are needed | React/Next.js data-flow, rendering, bundle, and performance constraints for `ENGINEERING.md` and implementation review | Generic frontend advice for Vue, Svelte, native mobile, server-rendered non-React, or undecided stacks |

## Sequence and conflict handling

For a new Web interface, use design intelligence first, then visual-direction critique. Record the synthesized and user-confirmed result in `DESIGN.md`; do not copy raw companion output wholesale.

Use implementation-specific guidance only after the stack is confirmed. When React or Next.js is selected, carry material `vercel-react-best-practices` constraints into `ENGINEERING.md` as project rules tied to actual architecture decisions. Do not record every generic rule.

Use `web-design-guidelines` after inspectable UI code or a rendered interface exists. Findings that change observable behavior return to `SPEC.md`; visual findings return to `DESIGN.md`; performance or coding constraints belong in `ENGINEERING.md` or `ARCHITECTURE.md`.

When recommendations conflict, apply this priority:

1. Explicit user requirements and confirmed project facts.
2. Approved PRD/SPEC/DESIGN/architecture decisions and applicable standards.
3. Task-specific companion-skill findings.
4. Generic defaults from any companion skill.

Record unresolved material conflicts as a stable TBD instead of silently choosing one skill's preference.

## Direction, handoff, and evidence return

At direction stage, use `frontend-design` to refine recognizable references, composition, visual hierarchy and key customization; use `ui-ux-pro-max` only for unresolved candidate or UX questions. Companion suggestions for exact palettes or dimensions remain exploratory until reviewed. Do not let a companion's preferred aesthetic or planning template override the selected direction.

At prototype stage, project-blueprint produces the lightweight component and representative-page preview, using `frontend-design` when available. Follow `design-and-architecture.md` for the default standalone HTML, project-route alternative, scope limits and human confirmation workflow. A larger prototype may be handed off to a frontend task, with links, revision/context and observations returned to the blueprint. Use `web-design-guidelines` on available UI for task/accessibility review, alongside visual critique. Agent checks inform human review; they do not confirm visual acceptance automatically.

At specification stage, derive tokens and component differences from accepted results or reuse approved design-system sources. Missing companions do not prevent lightweight preview generation using available tools. Missing generation/rendering capabilities leave an explicit gap and a usable artifact or handoff; never fabricate a passing review or require installation to continue.

## Installation handoff

If the user wants a reusable frontend setup, point them to the installation commands in the repository root `README.md`. Describe the three general Web skills as the frontend baseline and the React skill as conditional. Do not claim that installing `project-blueprint` installs them automatically.
