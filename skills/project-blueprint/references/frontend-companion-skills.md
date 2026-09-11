# Frontend companion skills

Use companion skills as a routed capability stack. They complement the blueprint contract; they do not replace confirmed product decisions, source verification, or the readiness gates.

## Dependency model

These are project-level companion skills, not application runtime packages and not automatic dependencies of `project-blueprint`. Do not add an unsupported `depends_on` field or list them under `agents/openai.yaml` `dependencies.tools`, which is reserved for tool dependencies.

If a relevant companion is installed, use it at the matching stage. If it is unavailable, continue with this skill's own design guidance and report the missing review or implementation capability in the handoff. Never install external skills silently while producing a blueprint.

## Routing

| Companion skill | Apply when | Contribution | Do not use as |
| --- | --- | --- | --- |
| `ui-ux-pro-max` | A Web or interactive client needs a design-system direction, palette/type/layout candidates, interaction patterns, or stack-aware UX guidance | Structured candidate generation and searchable UI/UX knowledge before finalizing `DESIGN.md` | An automatic final answer or evidence that a candidate fits the product without checking the brief |
| `frontend-design` | The work needs a distinctive visual thesis, hierarchy, typography, composition, or a critique of generic-looking UI | Subject-grounded visual direction and anti-template critique | A substitute for accessibility checks, behavioral specs, or confirmed brand constraints |
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

## Installation handoff

If the user wants a reusable frontend setup, point them to the installation commands in the repository root `README.md`. Describe the three general Web skills as the frontend baseline and the React skill as conditional. Do not claim that installing `project-blueprint` installs them automatically.
