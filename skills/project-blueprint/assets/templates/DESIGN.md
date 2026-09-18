---
blueprint_kind: design
blueprint_status: draft
design_stage: direction
owner: TBD-DESIGN-001
last_reviewed: YYYY-MM-DD
---

# Product Design Direction

Use only the sections needed at the current stage. `direction` establishes intent; `prototype` adds a viewable preview and human review; `specification` adds implementation definitions after acceptance. For a project without user-facing UI, use `not-applicable`, replace visual sections with an Applicability section explaining why, and keep behavior in SPEC. Delete these instructions from the output.

## Audience, context, and primary jobs

| Surface | Audience/context | Primary job | Evidence | State |
|---|---|---|---|---|

## Constraints and exploration space

- Functional invariants and source requirements:
- Confirmed brand requirements and provenance:
- Visual suggestions open to exploration:

## Information architecture and journeys

| Area/screen | User goal and content priority | Entry/exit | Related SPEC | State |
|---|---|---|---|---|

## Application shell and layout

Describe spatial relationships first. Keep layout family, navigation model, work-surface model, and platform chrome separate. SSO or unified login does not itself choose a sidebar. If unresolved, consult the layout catalog for plausible alternatives; if already chosen, record the decision without reopening selection.

- Composition and rationale; confirmed/provisional state:
- Global/local navigation, identity/context controls and work-surface relationship:
- Expanded/desktop anatomy and scroll ownership:
- Compact/mobile transformation and state continuity:
- Task result that would overturn the recommendation:

## Visual direction

- Visual thesis: how the primary job shapes hierarchy, typography, surface relationships and emphasis:
- Selected reference-led direction and rationale; confirmed/provisional state:
- References: what to borrow, what to adapt, and inspection status:
- Appearance and density by surface:
- Key customization: brand/accent direction, display/body relationship, composition and visual focus:
- Optional signature treatment grounded in the product:
- Decisions intentionally left for prototype exploration:

When the user specifies a direction, refine it directly. Otherwise compare two or three plausible options in plain language and recommend one. No mandatory theme IDs, weighted scores or complete token tables. Known brand values may be recorded; exploratory values remain provisional.

Present unresolved direction options in the conversation and obtain a choice or explicit delegation before calling the direction settled. Record the decision source, actual date and scope here; for a no-questions draft retain the provisional recommendation and pending selection. Direction selection is separate from the later visual review.

## Reference adaptation

Include when references inform the design; omit for an original direction without external references. Record only sources that change a decision. Identify the actual source page/surface and distinguish secondary analysis, inspected visuals, extracted values and estimates. Record source revision/access date and inspection limits. A collection entry is not an official brand specification or evidence of project approval.

| Reference and inspected evidence | Characteristic to borrow | Adopt / adapt / reject and task-based reason | Applicable surface and exclusions | Preview check / decision state |
|---|---|---|---|---|

If several references are used, name the primary composition and the bounded contribution of each secondary reference. Explain material conflicts, local font/content adaptations and unverified assumptions without copying whole external design systems.

## Design guardrails

Keep a few concrete, project-specific rules. During direction work mark exploratory choices provisional; after review link them to the accepted baseline. Existing approved rules may be referenced instead of repeated.

| Surface / element | Use | Avoid | Task or brand reason / source | State |
|---|---|---|---|---|

## Visual preview

At prototype stage, produce a lightweight preview after direction selection: default `design/preview.html`, or an existing project preview route/native prototype. Include project-relevant components and a representative business page. If delivery is deferred, omit Artifact and state the actual constraint plus owner and next step in Deferred reason. Remove unused fields; do not leave a link to a nonexistent artifact.

- Artifact:
- Preview revision and viewing/startup instructions:
- Components, variants and states demonstrated:
- Shared provisional token source for catalog/page, supported appearances and density scopes:
- Reference-derived decisions and where they can be judged:
- Representative page(s), primary task and acceptance owner:
- Real content or clearly labeled representative content and important states:
- Target devices: core desktop and narrow-screen views by default:
- Visual questions: hierarchy, spacing rhythm, style fidelity, brand recognition:
- Task, responsive and accessibility checks:
- Browser checks performed and unverified behavior:
- Deferred reason:
- Human review request: viewing link, revision, confirmation scope and unresolved questions:

## Visual review

Include at prototype stage onward. For a pending review, omit unavailable fields rather than inventing them. A confirmed review requires all fields below. Reused approved design-system evidence must identify its version or approval baseline, applicability and any project-specific deltas. Preserve the approved revision; material changes reopen the affected scope for review.

- Review status: pending
- Evidence:
- Reviewed revision:
- Confirmed scope:
- Reviewer:
- Reviewed on:
- Findings and adjustments:

## Responsive, states, and accessibility

- Responsive behavior and content priority:
- Loading/empty/error/permission/offline and destructive states relevant to the task:
- Keyboard/focus/touch, contrast, zoom and motion requirements:
- Content voice, labels, long text and localization:

## Icons, imagery, and Emoji

- Icon consistency and accessible labels:
- Imagery purpose, sources, rights and alternatives:
- Emoji policy: none by default in team-authored UI and system copy; document any approved exception with its scope, user value and accessible text/icon alternative.

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-DESIGN-001 | Confirm design owner and direction | [role/name] | [date/milestone] | implementation-ready | pending |
