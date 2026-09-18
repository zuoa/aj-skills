# Theme selection and framework adaptation

Use this catalog to recommend a visual direction from product evidence. It is a
shortlist, not a set of skins to apply unchanged. Brand assets, an existing
organizational design system, user research, and domain regulation take
precedence.

## Model themes as three independent axes

Do not create a separate theme for every combination. Record these axes
independently and compose them in `DESIGN.md`:

1. **Theme family** expresses product character and trust: for example
   `precision-neutral` or `editorial-paper`.
2. **Appearance** responds to environment and preference: `light`, `dark`,
   `system`, and, when required, a tested high-contrast/forced-colors path.
3. **Density** responds to task frequency and information volume:
   `comfortable`, `compact`, or a deliberately bounded responsive combination.

This mirrors durable open-source practice. shadcn/ui and daisyUI map semantic
names to CSS variables; Carbon keeps universal token roles stable across
themes; PrimeVue separates primitive, semantic, and component tokens; Ant
Design derives map and alias tokens from seed tokens and can compose dark and
compact algorithms. Appearance and density are therefore capabilities of a
theme system, not substitutes for a product-specific visual direction.

## Evidence to collect before recommending

| Input | Question that changes the recommendation |
|---|---|
| Product direction | Is this primarily a reading surface, transaction flow, expert workbench, monitoring console, or public/consumer experience? |
| Audience | Are users domain experts, occasional non-technical users, reviewers/approvers, developers, or members of the public? |
| Trust and consequence | Would a visual mistake merely feel off-brand, or could it obscure a financial, legal, health, security, or destructive state? |
| Information shape | Long-form Chinese text, forms, tables, charts, code, media, or mixed content? |
| Use environment | Session length, desktop/mobile mix, low-light use, field use, shared terminals, and display quality? |
| Brand evidence | Existing logo, palette, typography, screenshots, design system, and explicit references to borrow or avoid? |
| Delivery constraints | Framework, UI foundation, time, design capacity, bundle budget, SSR, localization, and upgrade ownership? |
| Accessibility | Required WCAG level, zoom/text scaling, forced-colors support, color-vision needs, motion sensitivity, and minimum target sizes? |

If these inputs are weak, provide a provisional recommendation and name the
revisit trigger. Do not infer a theme from industry stereotypes alone.

## Theme families

The values below are starter seeds for comparison, not a complete palette.
Use them only as optional exploration seeds. After representative-page acceptance,
derive semantic color, type, geometry and state definitions from the reviewed design
or an approved design system. Do not require these tables during direction work.

| ID and direction | Best fit and audience | Character and signature device | Starter light seeds: canvas / surface / text / accent | Density and appearance default | Framework fit and main risk |
|---|---|---|---|---|---|
| `precision-neutral` — precise knowledge tool | Developer tools, AI workbenches, technical documentation, professional productivity; expert or mixed technical audiences | Cool neutral surfaces, crisp grid, restrained blue action color. One useful signature may be a metadata rail or code-like provenance label. | `#F8FAFC` / `#FFFFFF` / `#172033` / `#2457D6` | Comfortable; `system` when dark mode can be verified | Strong with open-code/headless systems, Chakra, MUI, and PrimeVue presets. Risk: becoming a generic SaaS dashboard; tie the signature to provenance, versions, or workflow state. |
| `editorial-paper` — research and formal reading | Research, policy, legal, planning, reports, knowledge archives; reviewers and long-form readers | Warm paper, ink-first hierarchy, serif reserved for headings or reading content, quiet rules instead of card stacks. One signature may be margin annotations or source markers. | `#F7F3EA` / `#FFFDF7` / `#24211D` / `#8A3B32` | Comfortable; light first, dark only if long-screen use justifies it | Best with open-code/headless foundations because typography and document geometry dominate. Styled enterprise suites need more overrides. Risk: imitating print so closely that forms and focus states become weak. |
| `institutional-trust` — accountable service | Government/public service, healthcare administration, compliance, procurement, security, B2B approval flows; broad audiences | Low-chroma blue/navy, explicit boundaries, conventional navigation, strong status labels and audit cues. One signature may be a persistent case/status band. | `#F5F8FB` / `#FFFFFF` / `#17212B` / `#005EA8` | Comfortable; light default plus tested system/high-contrast behavior | Natural fit for MUI, Ant Design, PrimeVue, or Element Plus. Risk: default-library appearance; customize typography, spacing, status language, and domain artifacts before color decoration. |
| `operations-dense` — expert control surface | Monitoring, finance, inventory, analytics, incident response, internal admin; trained repeat users | Compact geometry, tabular numerals, stable columns, restrained teal/blue, status encoded with text and shape as well as color. One signature may be a real alert or timeline rail. | `#F3F5F7` / `#FFFFFF` / `#111827` / `#0F766E` | Compact on desktop, comfortable touch targets on mobile; `system`, with dark supported when low-light use is real | Strong with Ant Design compact algorithm, MUI/PrimeVue token overrides, or Element Plus. Risk: shrinking controls instead of increasing information efficiency; keep touch and focus requirements intact. |
| `calm-guidance` — approachable workflow | Education, onboarding, community tools, small-business workflows, wellbeing-adjacent non-clinical products; occasional or non-technical users | Warm neutral canvas, sage/teal action color, visible steps, generous error recovery, moderate radius. One signature may be a progress path that reflects the real workflow. | `#FAF8F3` / `#FFFFFF` / `#24312E` / `#25735F` | Comfortable; light default and optional system mode | Strong with Chakra, shadcn/ui, Radix Themes, or a customized PrimeVue preset. Risk: excessive rounded cards, illustrations, or reassuring copy that hides the actual task. |
| `expressive-studio` — brand-led creation | Creator tools, media, culture, campaign or consumer discovery experiences; audiences who value identity and exploration | High-contrast typography, restrained violet/coral accents, asymmetry limited to low-risk discovery surfaces. One signature may be a content-derived crop, frame, or editorial index. | `#FBF8FF` / `#FFFFFF` / `#251B35` / `#6D28D9` | Comfortable; appearance follows content and brand evidence | Best with open-code/headless systems or Chakra recipes. Styled enterprise suites can require costly anatomy overrides. Risk: applying expressive treatment to forms, destructive actions, dense tables, or regulated decisions. |

The six starter accent/white pairs were screened at 5.47:1–7.63:1. That is
only an initial normal-text contrast check; hover/pressed states, links on the
canvas, borders, focus indicators, status pairs, dark mode, and forced colors
still require independent verification.

### Direction-to-shortlist defaults

Use these only when stronger project evidence is absent:

| Product direction | First candidate | Credible alternative | When to change the order |
|---|---|---|---|
| Developer/AI/documentation product | `precision-neutral` | `operations-dense` | Put `expressive-studio` first only when public brand/discovery matters more than repeated work. |
| Research, legal, policy, or long-form knowledge | `editorial-paper` | `institutional-trust` | Put `institutional-trust` first for transactional public services, compliance, or broad accessibility needs. |
| Enterprise workflow or approval system | `institutional-trust` | `operations-dense` | Put `operations-dense` first for trained users handling many rows, alerts, or repeated actions. |
| Monitoring, finance, inventory, or analytics | `operations-dense` | `precision-neutral` | Prefer `precision-neutral` when interpretation and explanation dominate live control. |
| Education, onboarding, community, or SMB workflow | `calm-guidance` | `precision-neutral` | Prefer `institutional-trust` when consequences or formal accountability are high. |
| Creator, media, culture, or consumer discovery | `expressive-studio` | `calm-guidance` | Prefer `calm-guidance` when completion and reassurance matter more than exploration. |

For the AJ Skills repository itself, `precision-neutral` is the provisional
first recommendation: the audience spans developers and Chinese professional
knowledge workers, the material is documentation-heavy, and provenance,
compatibility, commands, and version state should be easier to scan than brand
decoration. `editorial-paper` is the stronger alternative for reading-focused
showcases of policy, research, legal, or planning outputs. This recommendation
must be revisited if the surface becomes a consumer marketplace rather than a
documentation/productivity site.

## Present a recognizable direction

A theme family is open vocabulary. A user can name Apple-site-like presentation,
an enterprise dark workbench, a cultural magazine, or another concrete reference;
do not translate it forcibly into one of the six families above. State which
reference characteristics to borrow and how they serve this product. Verify a
provided reference when accessible, and disclose when it has not been inspected.

For source selection and adaptation, use [design-reference-workflow.md](design-reference-workflow.md).
The optional awesome-design-md collection provides concrete analyses to inspect;
its brand names and extracted palettes are not additional fixed theme families.
Distinguish marketing-site references from actual workbench or native-screen
evidence, and record what the project adopts, changes and excludes.

If the user has selected a direction, refine its appearance, density, brand color,
typography relationship, composition and focal treatment without requiring an
alternative or scorecard. Otherwise show two or three credible options with a
plain-language tradeoff and one recommendation. Weights and numerical ratings
are not required. Consider task fit, audience, content, environment,
accessibility, distinctiveness and adaptation cost without pretending they
quantify visual taste.

Record key customization and what remains open for prototype exploration.
Compact content does not require a compact title or brand region. A dark theme
alone does not specify composition, and changing accent color alone does not
establish a visual identity. Compare representative pages before freezing values.

## UI-framework customization fit

Do not equate a framework preset with a product theme. Verify the current
official documentation during a blueprint run because APIs and primitive
foundations change.

| UI foundation | Customization model | Practical freedom | Best use | Cost/risk to record |
|---|---|---|---|---|
| shadcn/ui | Open-code components using semantic CSS variables, including background/foreground pairs and light/dark scopes | Very high; project owns markup and styling | Distinctive product UI, `precision-neutral`, `editorial-paper`, `calm-guidance`, `expressive-studio` | Ownership includes component updates, visual regression, token discipline, and merge decisions. |
| React Aria Components or Radix Primitives | Unstyled/headless accessible behavior with state hooks/data attributes; project supplies the visual system | Highest | Brand-specific anatomy or design-system teams able to own every visual layer | Highest design/implementation/QA cost; accessible primitives do not make custom compositions automatically accessible. |
| Radix Themes | Configurable appearance, accent/gray scales, radius, scaling, and panels over a styled system | Medium–high | Fast restrained product UI with bounded customization | Fastest within its visual grammar; unusual editorial or dense enterprise anatomy may need lower-level primitives. |
| Chakra UI | Primitive and semantic tokens plus typed recipes/slot recipes and conditional values | High | Product UI needing composable variants and enforceable token usage | Run type generation when tokens change; recipe and runtime styling constraints belong in the maintenance plan. |
| MUI | Theme configuration, CSS theme variables/color schemes, component variants and style overrides | High within Material component anatomy | Broad React coverage, institutional and enterprise workflows | Deep anatomy changes can accumulate overrides; document SSR color-scheme initialization and Material-look departures. |
| Ant Design | Seed → map → alias tokens, component tokens, and composable default/dark/compact algorithms | Medium–high within Ant component anatomy | Dense enterprise and operations products | Global/static API context, CSS-in-JS/runtime mode, and deep structural overrides require explicit verification. |
| daisyUI | Tailwind plugin with semantic CSS variables and multiple named themes | Medium–high for token-level changes | Fast multi-theme sites and conventional components | Easy palette switching can encourage theme sprawl; component anatomy and accessibility still need representative tests. |
| PrimeVue | Base plus preset; primitive, semantic, and component token tiers; configurable dark-mode selector | High | Vue enterprise/product UI across several theme families | Prefer a custom preset over scattered style-class overrides; record CSS layer, portal, and preset ownership. |
| Element Plus | SCSS maps plus global or scoped CSS variables and a class-based dark theme | Medium | Vue admin/enterprise UI with moderate brand adaptation | Component token documentation/coverage and deep override stability must be checked; large-scale CSS overrides raise upgrade cost. |
| Flutter Material | `ThemeData`, semantic `ColorScheme`, `TextTheme`, component themes, and theme extensions | High within Material anatomy | Cross-platform mobile apps that should retain native platform expectations | Seed generation is only a start; record platform adaptation, dynamic-color policy, custom-component extensions, and per-widget override growth. |
| Jetpack Compose Material 3 | `MaterialTheme` supplies color scheme, typography, shapes, and motion; components expose defaults for local adjustment | High within Material 3 anatomy | Android-first products and adaptive native UI | Dynamic color can dilute fixed brand/status colors; distinguish user personalization from safety-critical semantics and budget custom design systems when leaving Material anatomy. |
| React Native Paper | Provider theme based on Material 3 roles, light/dark themes, per-component theme props, and React Navigation adaptation | Medium–high within Material anatomy | React Native teams needing broad accessible mobile components quickly | Keep navigation and component providers on one semantic source; deep non-Material anatomy and platform-specific conventions raise override cost. |
| SwiftUI | Semantic asset colors and tint plus environment values for color scheme/contrast and custom environment-backed tokens | High at composition level, less prescriptive as a cross-platform token schema | Apple-native experiences that should follow system appearance and accessibility settings | The team must define and govern its own semantic token/component-style layer; do not force identical Web/Android geometry onto Apple platforms. |

### Required adapter decision

At specification stage, after accepting representative work, map the visual system to the
framework's primitive/semantic/component layers (or their equivalents) instead
of copying raw palette values through component code:

| Layer | Required decision |
|---|---|
| Primitive | Brand/neutral/status ramps, type families, spacing, radius, elevation, and motion scales. |
| Semantic | Canvas, surface, text, border, action, focus, disabled, and status roles for every supported appearance. Product code should consume these names. |
| Component | Only the deltas that cannot be expressed semantically: control height, table density, dialog geometry, selected tab treatment, and similar anatomy. |
| Mode and density | Selector/provider/algorithm, persistence, system preference, SSR/no-flash behavior, compact scope, and whether nested themes are allowed. |
| Governance | Source file, token prefix, allowed override mechanisms, visual-regression coverage, owner, upgrade cadence, and exceptions. |

Reject a candidate framework/theme pairing when achieving the direction needs
global descendant selectors, repeated `!important`, copied internal class
names, or widespread per-instance overrides. In that case choose a closer
theme family, a lower-level foundation, or explicitly budget a maintained fork.

## Cross-theme acceptance checks

- Verify normal text, large text, component boundaries, status pairs, and focus
  indicators against the project's WCAG target; do not approve a palette from
  swatches alone.
- Test light, dark, and any high-contrast/forced-colors behavior independently.
  Dark mode is not a mechanical inversion of light mode.
- Respect system appearance on first visit when supported, persist explicit user
  choice, declare `color-scheme`, and prevent a wrong-theme flash during SSR or
  hydration.
- Keep state understandable without color. In forced-colors mode, preserve the
  user's palette and make only targeted fixes.
- Test real Simplified Chinese copy, long Latin identifiers, tabular numbers,
  200% zoom, keyboard focus, reduced motion, and mobile touch targets.
- Review representative task screens, adding dialogs or status views where they
  materially test the direction. Do not force every component onto one showcase.
  A hero or button gallery alone cannot validate a workbench or content tool.

## Open-source references

Official sources checked 2026-09-11. Recheck current APIs and compatibility at
decision time.

- [shadcn/ui theming](https://ui.shadcn.com/docs/theming): semantic CSS
  variables, background/foreground token pairs, OKLCH values, and dark scopes.
- [daisyUI colors](https://daisyui.com/docs/colors/) and
  [themes](https://daisyui.com/docs/themes/): semantic colors and multiple
  CSS-variable themes, including a preferred dark theme.
- [Carbon themes](https://carbondesignsystem.com/elements/themes/overview/):
  stable universal tokens across white, gray, and dark themes.
- [PrimeVue styled mode](https://primevue.org/theming/styled/): base/preset
  separation; primitive, semantic, and component tokens; dark-mode selector.
- [Ant Design theme customization](https://ant.design/docs/react/customize-theme/):
  seed/map/alias and component tokens plus composable dark/compact algorithms.
- [MUI theming](https://mui.com/material-ui/customization/theming/) and
  [CSS theme-variable configuration](https://mui.com/material-ui/customization/css-theme-variables/configuration/):
  theme configuration, color schemes, CSS variables, runtime switching, and SSR
  flicker guidance.
- [Radix Themes overview](https://www.radix-ui.com/themes/docs/theme/overview)
  and [color system](https://www.radix-ui.com/themes/docs/theme/color):
  appearance, accent/gray scales, radius, scaling, and semantic scale anatomy.
- [Chakra UI semantic tokens](https://chakra-ui.com/docs/theming/semantic-tokens)
  and [recipes](https://chakra-ui.com/docs/theming/recipes): conditional
  semantic tokens and component variants.
- [Element Plus theming](https://element-plus.org/en-US/guide/theming) and
  [dark mode](https://element-plus.org/en-US/guide/dark-mode): SCSS/CSS-variable
  customization and dark-theme scoping.
- [React Aria styling](https://react-spectrum.adobe.com/react-aria/getting-started.html#styling):
  unstyled accessible components with exposed interaction states.
- [Flutter styling](https://docs.flutter.dev/ui/widgets/styling): `ThemeData`,
  color schemes, typography, and component theming.
- [Jetpack Compose Material 3](https://developer.android.com/develop/ui/compose/designsystems/material3):
  `MaterialTheme`, semantic color roles, typography, shapes, component defaults,
  light/dark, and optional dynamic color.
- [React Native Paper theming](https://callstack.github.io/react-native-paper/docs/guides/theming-with-react-navigation):
  Material 3 light/dark themes, providers, component theme access, and navigation
  theme adaptation.
- [SwiftUI `EnvironmentValues`](https://developer.apple.com/documentation/SwiftUI/EnvironmentValues)
  and [`ColorScheme`](https://developer.apple.com/documentation/swiftui/colorscheme):
  system appearance and contrast values available to view hierarchies.
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/),
  [MDN `color-scheme`](https://developer.mozilla.org/en-US/docs/Web/CSS/color-scheme),
  and [MDN `forced-colors`](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/forced-colors):
  accessibility criteria and browser/user preference behavior.
