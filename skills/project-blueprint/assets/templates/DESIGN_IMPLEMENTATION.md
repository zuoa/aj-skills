# Implementation specification supplement

Merge applicable sections into DESIGN.md only after visual acceptance and set `design_stage: specification`. This is a template fragment, not a new mandatory project artifact. Link to maintained definitions rather than copying them. Remove unused rows and instructional placeholders.

## Token source

- Authoritative source: [link to theme/config/design system, or an inline section anchor]
- Supported appearance and density:
- Ownership and permitted overrides:
- Mapping from the accepted preview baseline to this source; known differences and verification:

Keep exact definitions in one maintained source. The component catalog and business-page preview must use that source or a documented equivalent. Do not duplicate the token set across Markdown, nested frontmatter and CSS; keep blueprint frontmatter for metadata.

## Color system

- Palette rationale and relationship to the primary job:
- Theme strategy: [light / dark / system; default]
- Color notation and gamut policy: [HEX / OKLCH / other]

| Token | Light value | Dark value | Semantic role and allowed use | Interaction/contrast requirement | State |
|---|---|---|---|---|---|
| `color-canvas` | [exact value] | [exact value or N/A] | App/page background | With primary text: [target] | [state] |
| `color-surface` | [exact value] | [exact value or N/A] | Default component surface | With body text: [target] | [state] |
| `color-surface-raised` | [exact value] | [exact value or N/A] | Dialog/popover/raised surface | Distinguishable without relying on shadow alone | [state] |
| `color-text-primary` | [exact value] | [exact value or N/A] | Primary text | Against canvas/surface: [target] | [state] |
| `color-text-secondary` | [exact value] | [exact value or N/A] | Supporting text | Against canvas/surface: [target] | [state] |
| `color-border` | [exact value] | [exact value or N/A] | Dividers and control boundaries | Boundary remains visible in required modes | [state] |
| `color-action-primary` | [exact value] | [exact value or N/A] | Primary action and selected state; brand accents may use a separate role | Default state; text: [target] | [state] |
| `color-action-primary-hover` | [exact value] | [exact value or N/A] | Primary action hover | Distinct from default without shifting layout | [state] |
| `color-action-primary-pressed` | [exact value] | [exact value or N/A] | Primary action pressed | Distinct from hover and default | [state] |
| `color-text-on-action` | [exact value] | [exact value or N/A] | Text/icon on primary action | Against all action states: [target] | [state] |
| `color-focus-ring` | [exact value] | [exact value or N/A] | Keyboard focus | Visible against canvas and every component surface | [state] |
| `color-disabled` | [exact value] | [exact value or N/A] | Disabled content/control | Never the only disabled cue | [state] |
| `color-success` | [foreground + surface exact values] | [foreground + surface exact values or N/A] | Successful outcome | Text/icon on status surface: [target] | [state] |
| `color-warning` | [foreground + surface exact values] | [foreground + surface exact values or N/A] | Recoverable risk | Text/icon on status surface: [target] | [state] |
| `color-error` | [foreground + surface exact values] | [foreground + surface exact values or N/A] | Error/destructive outcome | Text/icon on status surface: [target] | [state] |
| `color-info` | [foreground + surface exact values] | [foreground + surface exact values or N/A] | Neutral information | Text/icon on status surface: [target] | [state] |

Derive these values from the accepted page or link to the approved semantic palette. Include only supported modes and used roles. Do not fill duplicate tables when the maintained source already defines them.

## Typography system

- Base/root size and scaling policy:
- UI/body font stack, language fallbacks, and rationale:
- Display/brand font stack, if different:
- Monospace or tabular-numeric policy:
- Font source, license, loading/fallback, and layout-shift policy:

| Type token | Font family/token | Desktop size / line height | Mobile size / line height | Weight | Letter spacing | Intended use | State |
|---|---|---|---|---|---|---|---|
| `type-display` | [font stack/token] | [rem + px reference] | [rem + px reference] | [number] | [value] | Display emphasis where supported by the accepted composition, or N/A | [state] |
| `type-page-title` | [font stack/token] | [rem + px reference] | [rem + px reference] | [number] | [value] | One page-level heading | [state] |
| `type-section-title` | [font stack/token] | [rem + px reference] | [rem + px reference] | [number] | [value] | Section headings | [state] |
| `type-body` | [font stack/token] | [rem + px reference] | [rem + px reference] | [number] | [value] | Default reading/UI text | [state] |
| `type-body-small` | [font stack/token] | [rem + px reference] | [rem + px reference] | [number] | [value] | Secondary content | [state] |
| `type-label` | [font stack/token] | [rem + px reference] | [rem + px reference] | [number] | [value] | Form and field labels | [state] |
| `type-action` | [font stack/token] | [rem + px reference] | [rem + px reference] | [number] | [value] | Buttons and action links | [state] |
| `type-helper` | [font stack/token] | [rem + px reference] | [rem + px reference] | [number] | [value] | Help, validation, error text | [state] |
| `type-data` | [font stack/token] | [rem + px reference] | [rem + px reference] | [number] | [value] | Tables, timestamps, amounts, IDs | [state] |

## UI foundation and component sourcing

For a React or Vue client, select one coherent UI foundation before implementation. Do not treat unthemed browser-default controls or a list of undecided libraries as the finished component strategy. If a library is genuinely unnecessary, mark it `not-applicable` and document how complex interaction and accessibility behavior will be supplied and tested.

| Client/stack | Candidate foundations | Selected foundation and mode | Theme customization model and fit | Constraint-based rationale / rejected alternative | Official compatibility evidence and access date | State |
|---|---|---|---|---|---|---|
| [React / Vue / other] | [at least two credible options, or existing organizational system] | [named system; styled / open-code / headless / organizational] | [primitive/semantic/component token equivalents; appearance/density/scoping; permitted overrides; adaptation cost] | [fit, cost, and why the alternative lost] | [official source; YYYY-MM-DD] | [state] |

| Concern | Decision | Verification / ownership | State |
|---|---|---|---|
| Theme and token entry point | [preset/config/CSS variables and override boundary] | [representative screen + owner] | [state] |
| Appearance, density, and scoping | [system/manual mode, persistence, SSR/no-flash, compact scope, nested-theme policy] | [first render + mode/density matrix] | [state] |
| Component coverage | [map required Select/Combobox, Menu, Tabs, Dialog/Drawer, Toast/Alert, Table/Pagination, form behavior] | [keyboard/focus/visual regression tests] | [state] |
| Icon system | [one SVG icon set; sizing and accessible-name rule] | [lint/review owner] | [state] |
| Runtime and delivery | [bundle/import, SSR/hydration, localization, portal/z-index implications] | [build/profile/test evidence] | [state] |
| Dependency maintenance | [version/range, update cadence, exception policy] | [owner and revisit trigger] | [state] |

## Component specifications

Map used components to shared tokens or named foundation variants. Record only project-specific differences and relevant state behavior; do not repeat resolved font stacks or numbers. Omit unused components. Token and variant references must resolve through the source above.

| Component / part | Shared tokens or foundation variant | Product-specific geometry/style deltas | Required states and behavior | Source/override | State |
|---|---|---|---|---|---|
| [used component] | [documented reference] | [delta or inherit] | [relevant states] | [source/rule] | [state] |

## Remaining design tokens

| Topic | Source/decision | Product-specific override | State |
|---|---|---|---|
| Spacing/grid and content widths | | | |
| Responsive breakpoints | | | |
| Radius/border/elevation | | | |
| Motion duration/easing | | | |

## Surface hierarchy and depth

Describe how the accepted design distinguishes canvas, content regions, selected/raised elements and overlays using surface, border, radius and elevation together. Include only used layers; link existing theme definitions rather than repeating values. A light page containing a dark region does not imply support for a full dark theme.

| Layer / actual use | Shared surface, border and elevation tokens | Relationship to adjacent layers | Appearance / focus considerations |
|---|---|---|---|

## Agent implementation brief

Keep this brief short enough to use directly in a frontend task. Replace these prompts with project-specific links and instructions, then remove them. This section routes to authoritative rules and does not create another copy of the design system.

- Implement the linked [SPEC/task and target page] within its confirmed behavior and scope.
- Match [accepted preview or approved system] at [reviewed revision], covering [accepted components, states, viewports and appearances].
- Use [Token source], [Component specifications] and [Design guardrails]; preserve the visual thesis and named product-specific differences.
- Respect [pending decisions / excluded scope]; do not treat reference-site features or unreviewed modes as approved requirements.
- Check the representative page, required states, long/localized content, responsive behavior and applicable accessibility criteria; record actual results and the tested revision.
- Iterate against that baseline. Material visual changes return to review before updating acceptance and dependent implementation readiness.
