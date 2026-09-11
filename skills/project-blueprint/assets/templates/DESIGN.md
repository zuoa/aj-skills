---
blueprint_kind: design
blueprint_status: draft
owner: TBD-DESIGN-001
last_reviewed: YYYY-MM-DD
---

# Product Design Constraints

## Audience, context, and primary jobs

| Surface | Audience/context | Primary job | Evidence | State |
|---|---|---|---|---|

## Experience principles

| Principle | User consequence | Anti-pattern | State |
|---|---|---|---|

## Information architecture and journeys

| Area/screen | User goal | Entry/exit | Related SPEC | State |
|---|---|---|---|---|

## Visual direction

- Visual thesis and task rationale:
- Signature device (one maximum):
- References, what to borrow, and why:
- Explicitly avoid and why:
- Spacing/grid/density/radius/elevation:
- Motion and imagery:

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
| `color-action-primary` | [exact value] | [exact value or N/A] | Primary action and selected state only | Default state; text: [target] | [state] |
| `color-action-primary-hover` | [exact value] | [exact value or N/A] | Primary action hover | Distinct from default without shifting layout | [state] |
| `color-action-primary-pressed` | [exact value] | [exact value or N/A] | Primary action pressed | Distinct from hover and default | [state] |
| `color-text-on-action` | [exact value] | [exact value or N/A] | Text/icon on primary action | Against all action states: [target] | [state] |
| `color-focus-ring` | [exact value] | [exact value or N/A] | Keyboard focus | Visible against canvas and every component surface | [state] |
| `color-disabled` | [exact value] | [exact value or N/A] | Disabled content/control | Never the only disabled cue | [state] |
| `color-success` | [foreground + surface exact values] | [foreground + surface exact values or N/A] | Successful outcome | Text/icon on status surface: [target] | [state] |
| `color-warning` | [foreground + surface exact values] | [foreground + surface exact values or N/A] | Recoverable risk | Text/icon on status surface: [target] | [state] |
| `color-error` | [foreground + surface exact values] | [foreground + surface exact values or N/A] | Error/destructive outcome | Text/icon on status surface: [target] | [state] |
| `color-info` | [foreground + surface exact values] | [foreground + surface exact values or N/A] | Neutral information | Text/icon on status surface: [target] | [state] |

If brand inputs are missing, choose an accessible provisional palette with exact values and a revisit trigger. Do not replace the table with “use brand colors” or leave implementation tokens blank.

## Typography system

- Base/root size and scaling policy:
- UI/body font stack, language fallbacks, and rationale:
- Display/brand font stack, if different:
- Monospace or tabular-numeric policy:
- Font source, license, loading/fallback, and layout-shift policy:

| Type token | Font family/token | Desktop size / line height | Mobile size / line height | Weight | Letter spacing | Intended use | State |
|---|---|---|---|---|---|---|---|
| `type-display` | [font stack/token] | [rem + px reference] | [rem + px reference] | [number] | [value] | Marketing/hero only, or N/A | [state] |
| `type-page-title` | [font stack/token] | [rem + px reference] | [rem + px reference] | [number] | [value] | One page-level heading | [state] |
| `type-section-title` | [font stack/token] | [rem + px reference] | [rem + px reference] | [number] | [value] | Section headings | [state] |
| `type-body` | [font stack/token] | [rem + px reference] | [rem + px reference] | [number] | [value] | Default reading/UI text | [state] |
| `type-body-small` | [font stack/token] | [rem + px reference] | [rem + px reference] | [number] | [value] | Secondary content | [state] |
| `type-label` | [font stack/token] | [rem + px reference] | [rem + px reference] | [number] | [value] | Form and field labels | [state] |
| `type-action` | [font stack/token] | [rem + px reference] | [rem + px reference] | [number] | [value] | Buttons and action links | [state] |
| `type-helper` | [font stack/token] | [rem + px reference] | [rem + px reference] | [number] | [value] | Help, validation, error text | [state] |
| `type-data` | [font stack/token] | [rem + px reference] | [rem + px reference] | [number] | [value] | Tables, timestamps, amounts, IDs | [state] |

## Component specifications

Include every component used by the defined screens. The rows below are the minimum review set; mark genuinely unused rows `not-applicable` and add product-specific components.

| Component / part | Type token | Resolved font family | Size / line height / weight | Height/padding/gap | Radius/border/elevation | Required states and behavior | Source/override | State |
|---|---|---|---|---|---|---|---|---|
| Button: label | [`type-action`] | [full resolved stack] | [exact values] | [exact values] | [tokens/values] | default, hover, focus, pressed, disabled, loading | [source/rule] | [state] |
| Input/Select: label, value, helper/error | [tokens per part] | [full resolved stack] | [exact values per part] | [exact values] | [tokens/values] | empty, filled, hover, focus, invalid, disabled, read-only | [source/rule] | [state] |
| Navigation/Tabs: item and badge | [tokens per part] | [full resolved stack] | [exact values per part] | [exact values] | [tokens/values] | default, hover, focus, current, overflow | [source/rule] | [state] |
| Table/List: header, cell, metadata | [tokens per part] | [full resolved stack] | [exact values per part] | [row density values] | [tokens/values] | loading, empty, selected, sorted, truncated, responsive | [source/rule] | [state] |
| Card: title, body, metadata | [tokens per part] | [full resolved stack] | [exact values per part] | [exact values] | [tokens/values] | default, interactive, selected, disabled | [source/rule] | [state] |
| Dialog/Drawer: title, body, actions | [tokens per part] | [full resolved stack] | [exact values per part] | [exact values] | [tokens/values] | opened, initial focus, overflow, closing, destructive confirmation | [source/rule] | [state] |
| Toast/Alert: title, body, action | [tokens per part] | [full resolved stack] | [exact values per part] | [exact values] | [tokens/values] | info, success, warning, error, timeout/persistent | [source/rule] | [state] |

## Icons, imagery, and Emoji

- Icon source and labeling policy:
- Imagery source, rights, and accessibility:
- Emoji policy: none by default in team-authored UI and system copy.

| Emoji exception/use location | User value | Text/icon alternative | Approver and state |
|---|---|---|---|

## Remaining design tokens

| Topic | Source/decision | Override policy | State |
|---|---|---|---|
| Spacing and layout grid | | | |
| Breakpoints and content widths | | | |
| Radius | | | |
| Border and elevation | | | |
| Motion duration/easing | | | |

## Responsive and platform behavior

| Context | Layout/input/safe-area behavior | Related SPEC | State |
|---|---|---|---|

## UI state matrix

| Flow/screen | Loading | Empty | Error | Offline | Permission | Destructive action |
|---|---|---|---|---|---|---|

## Accessibility and content

- Accessibility target:
- Keyboard/focus/touch targets:
- Contrast and non-color cues:
- Screen reader/semantic behavior:
- Localization and text expansion:
- Content voice and terminology:

## Design self-critique

- Product-specific choices that would not transfer unchanged to an unrelated product:
- Structural elements and the information they encode:
- Decoration or familiar AI-design patterns removed or explicitly justified:
- Evidence and acceptance method for the riskiest design assumption:

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-DESIGN-001 | Confirm design owner and direction | [role/name] | [date/milestone] | implementation-ready | pending |
